"""Exercise TLS record buffering through the normal NETCONF manager."""

import socket
import ssl
import threading
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import pytest
from lxml import etree

from ncclient import manager
from ncclient.transport.session import Session


CERTS = Path(__file__).parent / 'certs'
NS = 'urn:ietf:params:xml:ns:netconf:base:1.0'
DELIM = b']]>]]>'


def receive_message(sock, chunked=False):
    data = b''
    terminator = b'\n##\n' if chunked else DELIM
    while not data.endswith(terminator):
        chunk = sock.recv(4096)
        if not chunk:
            raise EOFError('client disconnected before sending a message')
        data += chunk
    if chunked:
        header, data = data[2:].split(b'\n', 1)
        length = int(header)
        assert data[length:] == terminator
        return data[:length]
    return data[:-len(DELIM)]


@contextmanager
def netconf_server(hello_padding, reply_padding, chunked,
                   close_after_reply=False):
    """Keep the peer open so EOF readiness cannot conceal buffered data."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(str(CERTS / 'loopback.crt'),
                            str(CERTS / 'test.key'))
    context.load_verify_locations(str(CERTS / 'loopback.crt'))
    context.verify_mode = ssl.CERT_REQUIRED
    release = threading.Event()
    errors = []
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    listener.settimeout(5)

    def serve():
        try:
            raw, _ = listener.accept()
            with raw, context.wrap_socket(raw, server_side=True) as peer:
                peer.settimeout(5)
                assert peer.getpeercert()
                receive_message(peer)
                capabilities = '<capability>%s</capability>' % NS
                if chunked:
                    capabilities += ('<capability>urn:ietf:params:netconf:'
                                     'base:1.1</capability>')
                hello = ('<hello xmlns="%s"><capabilities>%s'
                         '<capability>urn:test:%s</capability>'
                         '</capabilities><session-id>42</session-id></hello>'
                         % (NS, capabilities, 'h' * hello_padding)).encode()
                # One TLS application record, larger than the client's recv.
                assert len(hello) < 16384
                peer.sendall(hello + DELIM)
                request = etree.fromstring(receive_message(peer, chunked))
                reply = ('<rpc-reply xmlns="%s" message-id="%s">'
                         '<data><value>%s</value></data></rpc-reply>'
                         % (NS, request.get('message-id'),
                            'r' * reply_padding)).encode()
                assert len(reply) < 16384
                if chunked:
                    reply = b'\n#%i\n' % len(reply) + reply + b'\n##\n'
                else:
                    reply += DELIM
                peer.sendall(reply)
                if not close_after_reply:
                    release.wait(5)
        except Exception as error:
            errors.append(error)

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    completed = False
    try:
        yield listener.getsockname()[1]
        completed = True
    finally:
        release.set()
        listener.close()
        thread.join(6)
        assert not thread.is_alive()
        if completed:
            assert not errors, errors


@pytest.mark.parametrize('chunked', [False, True])
@pytest.mark.parametrize('hello_padding,reply_padding', [
    (9000, 1), (1, 9000), (9000, 9000), (1, 1),
])
def test_tls_buffered_hello_and_rpc(hello_padding, reply_padding, chunked):
    post_connect = Session._post_connect

    def bounded_hello(session):
        try:
            return post_connect(session, timeout=2)
        except Exception:
            session.close()
            raise

    with netconf_server(hello_padding, reply_padding, chunked) as port:
        connection = None
        try:
            with patch.object(Session, '_post_connect', bounded_hello):
                connection = manager.connect_tls(
                    host='127.0.0.1', port=port,
                    certfile=str(CERTS / 'loopback.crt'),
                    keyfile=str(CERTS / 'test.key'),
                    ca_certs=str(CERTS / 'loopback.crt'),
                    protocol=ssl.PROTOCOL_TLS_CLIENT,
                    timeout=2,
                    manager_params={'timeout': 2})
            assert connection.session_id == '42'
            assert 'urn:test:' + 'h' * hello_padding in (
                connection.server_capabilities)
            response = connection.get()
            assert response.ok
            value = response.data_ele.find('{%s}value' % NS)
            assert value.text == 'r' * reply_padding
        finally:
            if connection is not None:
                connection._session.close()


@pytest.mark.parametrize('chunked', [False, True])
def test_tls_peer_closes_after_buffered_reply(chunked):
    with netconf_server(1, 9000, chunked, close_after_reply=True) as port:
        connection = manager.connect_tls(
            host='127.0.0.1', port=port,
            certfile=str(CERTS / 'loopback.crt'),
            keyfile=str(CERTS / 'test.key'),
            ca_certs=str(CERTS / 'loopback.crt'),
            protocol=ssl.PROTOCOL_TLS_CLIENT, timeout=2,
            manager_params={'timeout': 2})
        try:
            response = connection.get()
            assert response.data_ele.find('{%s}value' % NS).text == 'r' * 9000
            connection._session.join(2)
            assert not connection._session.is_alive()
            assert not connection.connected
        finally:
            connection._session.close()
