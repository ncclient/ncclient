"""Exercise TLS address selection through a real NETCONF manager."""

import socket
import ssl
import threading
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from lxml import etree

from ncclient import manager
from ncclient.transport.errors import TLSError
from ncclient.transport.session import Session
from ncclient.transport.tls import TLSSession


CERTS = Path(__file__).parent / 'certs'
CERT = str(CERTS / 'ipv6-loopback.crt')
KEY = str(CERTS / 'test.key')
NS = 'urn:ietf:params:xml:ns:netconf:base:1.0'
DELIM = b']]>]]>'


def receive_message(peer):
    data = b''
    while not data.endswith(DELIM):
        chunk = peer.recv(4096)
        if not chunk:
            raise EOFError('client disconnected before sending a message')
        data += chunk
    return data[:-len(DELIM)]


def listener_for(family):
    listener = socket.socket(family, socket.SOCK_STREAM)
    try:
        if family == socket.AF_INET6:
            listener.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        listener.bind(('::1' if family == socket.AF_INET6 else '127.0.0.1', 0))
    except OSError:
        listener.close()
        if family == socket.AF_INET6:
            pytest.skip('IPv6 loopback is unavailable')
        raise
    listener.listen(1)
    listener.settimeout(0.1)
    return listener


@contextmanager
def netconf_server(family, exchange=True):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT, KEY)
    context.load_verify_locations(CERT)
    context.verify_mode = ssl.CERT_REQUIRED
    observed = {'sni': [], 'errors': []}
    context.set_servername_callback(
        lambda peer, hostname, ctx: observed['sni'].append(hostname))
    listener = listener_for(family)
    release = threading.Event()

    def serve():
        try:
            while not release.is_set():
                try:
                    raw, _ = listener.accept()
                    break
                except socket.timeout:
                    continue
            else:
                return
            with raw:
                raw.settimeout(2)
                with context.wrap_socket(raw, server_side=True) as peer:
                    observed['client_certificate'] = peer.getpeercert()
                    if not exchange:
                        return
                    hello = etree.fromstring(receive_message(peer))
                    assert hello.tag == '{%s}hello' % NS
                    peer.sendall((
                        '<hello xmlns="%s"><capabilities><capability>%s'
                        '</capability></capabilities><session-id>42'
                        '</session-id></hello>' % (NS, NS)).encode() + DELIM)
                    request = etree.fromstring(receive_message(peer))
                    assert request.find('{%s}get' % NS) is not None
                    peer.sendall((
                        '<rpc-reply xmlns="%s" message-id="%s">'
                        '<data><value>ipv6</value></data></rpc-reply>'
                        % (NS, request.get('message-id'))).encode() + DELIM)
                    release.wait(3)
        except Exception as error:
            observed['errors'].append(error)

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    completed = False
    try:
        yield listener.getsockname()[1], observed
        completed = True
    finally:
        release.set()
        thread.join(3)
        listener.close()
        assert not thread.is_alive()
        if completed and exchange:
            assert not observed['errors'], observed['errors']
            assert observed['client_certificate']


def connect(host, port, **kwargs):
    return manager.connect_tls(
        host=host, port=port, certfile=CERT, keyfile=KEY, ca_certs=CERT,
        protocol=ssl.PROTOCOL_TLS_CLIENT, timeout=1,
        manager_params={'timeout': 2}, **kwargs)


@contextmanager
def bounded_hello():
    post_connect = Session._post_connect

    def post(session):
        try:
            return post_connect(session, timeout=2)
        except Exception:
            session.close()
            raise

    with patch.object(Session, '_post_connect', post):
        yield


def exchange(host, port, **kwargs):
    with bounded_hello():
        connection = connect(host, port, **kwargs)
    try:
        assert connection.session_id == '42'
        assert connection._session.host == host
        reply = connection.get()
        assert reply.data_ele.find('{%s}value' % NS).text == 'ipv6'
    finally:
        # Wake the existing session loop before closing its descriptor.
        connection._session._closing.set()
        connection._session._socket.shutdown(socket.SHUT_RDWR)
        connection._session.join(2)
        connection._session.close()
        assert not connection._session.is_alive()


@pytest.mark.parametrize('family,host,kwargs,sni', [
    (socket.AF_INET, '127.0.0.1', {}, None),
    (socket.AF_INET, '127.0.0.1',
     {'server_hostname': 'localhost'}, 'localhost'),
    (socket.AF_INET6, '::1', {}, None),
    (socket.AF_INET6, '::1', {'server_hostname': 'localhost'}, 'localhost'),
    (socket.AF_INET6, '::1',
     {'check_hostname': False, 'server_hostname': 'other.example'},
     'other.example'),
])
def test_tls_hello_and_rpc(family, host, kwargs, sni):
    with netconf_server(family) as (port, observed):
        exchange(host, port, **kwargs)
        assert observed['sni'] == [sni]


def test_tls_aaaa_only_hostname():
    with netconf_server(socket.AF_INET6) as (port, observed):
        addresses = [(socket.AF_INET6, socket.SOCK_STREAM,
                      socket.IPPROTO_TCP, '', ('::1', port, 0, 0))]
        with patch('socket.getaddrinfo', return_value=addresses) as resolve:
            exchange('localhost', port)
        resolve.assert_called_once_with('localhost', port, 0,
                                        socket.SOCK_STREAM)
        assert observed['sni'] == ['localhost']


def test_tls_falls_back_to_second_address():
    # Reserve the same IPv6 port without listening: its connect must fail,
    # while the second (IPv4) address is a real, mutually authenticated peer.
    with netconf_server(socket.AF_INET) as (port, observed):
        refused = listener_for(socket.AF_INET6)
        refused.close()
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as refused:
            refused.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
            refused.bind(('::1', port))
            addresses = [
                (socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP,
                 '', ('::1', port, 0, 0)),
                (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP,
                 '', ('127.0.0.1', port)),
            ]
            created = []
            socket_type = socket.socket

            def retain(*args, **kwargs):
                sock = socket_type(*args, **kwargs)
                created.append(sock)
                return sock

            resolver = patch('socket.getaddrinfo', return_value=addresses)
            with resolver as resolve:
                with patch('socket.socket', side_effect=retain):
                    exchange('localhost', port)
            failed = [s for s in created if s.family == socket.AF_INET6]
            assert failed
            assert all(s.fileno() == -1 for s in failed)
            resolve.assert_called_once_with('localhost', port, 0,
                                            socket.SOCK_STREAM)
            assert observed['sni'] == ['localhost']


@pytest.mark.parametrize('kwargs', [
    {'server_hostname': 'other.example'},
    {'ca_certs': str(CERTS / 'test.crt')},
    {'ca_certs': str(CERTS / 'test.crt'), 'check_hostname': False},
])
def test_tls_verification_failure_closes_socket(kwargs):
    sockets = []
    wrap = ssl.SSLContext.wrap_socket

    def retain(context, *args, **options):
        sock = wrap(context, *args, **options)
        sockets.append(sock)
        return sock

    options = dict(host='127.0.0.1', certfile=CERT, keyfile=KEY,
                   ca_certs=CERT, protocol=ssl.PROTOCOL_TLS_CLIENT, timeout=1)
    options.update(kwargs)
    with netconf_server(socket.AF_INET, exchange=False) as (port, _):
        with patch.object(ssl.SSLContext, 'wrap_socket', retain):
            with pytest.raises(TLSError, match='Unsuccessful TLS handshake'):
                TLSSession(MagicMock()).connect(port=port, **options)
        # Inspect retained objects before garbage collection can hide a leak.
        assert sockets
        assert all(sock.fileno() == -1 for sock in sockets)


def test_tls_dns_failure_preserves_connection_error():
    error = socket.gaierror('no address')
    with patch('socket.getaddrinfo', side_effect=error):
        with pytest.raises(TLSError, match='Could not connect to absent:6513'):
            TLSSession(MagicMock()).connect(
                host='absent', certfile=CERT, keyfile=KEY, ca_certs=CERT,
                protocol=ssl.PROTOCOL_TLS_CLIENT)


def test_tls_wrap_failure_closes_raw_socket():
    with socket.socket() as raw:
        with patch('socket.create_connection', return_value=raw) as create:
            with patch.object(ssl.SSLContext, 'wrap_socket',
                              side_effect=ValueError('cannot wrap')):
                with pytest.raises(ValueError, match='cannot wrap'):
                    TLSSession(MagicMock()).connect(
                        host='localhost', certfile=CERT, keyfile=KEY,
                        ca_certs=CERT, protocol=ssl.PROTOCOL_TLS_CLIENT,
                        timeout=3)
            create.assert_called_once_with(('localhost', 6513), timeout=3)
            assert raw.fileno() == -1


def test_tls_handshake_timeout_closes_socket():
    sockets = []
    wrap = ssl.SSLContext.wrap_socket

    def retain(context, *args, **options):
        sock = wrap(context, *args, **options)
        sockets.append(sock)
        return sock

    # TCP connects to the listening socket, but no TLS peer consumes the hello.
    with listener_for(socket.AF_INET) as listener:
        with patch.object(ssl.SSLContext, 'wrap_socket', retain):
            with pytest.raises(TLSError, match='Unsuccessful TLS handshake'):
                TLSSession(MagicMock()).connect(
                    host='127.0.0.1', port=listener.getsockname()[1],
                    certfile=CERT, keyfile=KEY, ca_certs=CERT,
                    protocol=ssl.PROTOCOL_TLS_CLIENT, timeout=0.05)
        assert sockets
        assert all(sock.fileno() == -1 for sock in sockets)
