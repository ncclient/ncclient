"""NETCONF hello framing with a real SSH peer and delayed send credit."""

import socket
import threading
from contextlib import contextmanager
from pathlib import Path

import paramiko
import pytest
from lxml import etree
from paramiko.common import cMSG_CHANNEL_WINDOW_ADJUST

from ncclient import manager


NS = 'urn:ietf:params:xml:ns:netconf:base:1.0'
DELIM = b']]>]]>'
KEY = Path(__file__).parent / 'certs' / 'test.key'


class NetconfServer(paramiko.ServerInterface):
    def __init__(self):
        self.subsystem = threading.Event()

    def check_auth_password(self, username, password):
        if username == 'test' and password == 'test':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_request(self, kind, channel_id):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_subsystem_request(self, channel, name):
        if name == 'netconf':
            self.subsystem.set()
            return True
        return False


def receive_message(channel):
    data = b''
    while not data.endswith((DELIM, b'\n##\n')):
        chunk = channel.recv(4096)
        if not chunk:
            raise EOFError('client disconnected')
        data += chunk
    return data


@contextmanager
def ssh_server(delayed, chunked):
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    listener.settimeout(5)
    credit = threading.Event()
    release = threading.Event()
    errors = []
    received = []
    hello_received = threading.Event()

    def serve():
        try:
            sock, _ = listener.accept()
            with sock, paramiko.Transport(
                    sock, default_window_size=0 if delayed else 32768
            ) as transport:
                transport.add_server_key(
                    paramiko.RSAKey.from_private_key_file(str(KEY)))
                server = NetconfServer()
                transport.start_server(server=server)
                channel = transport.accept(5)
                assert channel is not None
                channel.settimeout(5)
                assert server.subsystem.wait(5)
                capabilities = '<capability>%s</capability>' % NS
                if chunked:
                    capabilities += ('<capability>urn:ietf:params:netconf:'
                                     'base:1.1</capability>')
                channel.sendall((
                    '<hello xmlns="%s"><capabilities>%s</capabilities>'
                    '<session-id>42</session-id></hello>' % (NS, capabilities)
                ).encode() + DELIM)
                if delayed:
                    assert credit.wait(5)
                    # Release normal SSH window credit after capability
                    # negotiation, without changing ncclient's send loop.
                    update = paramiko.Message()
                    update.add_byte(cMSG_CHANNEL_WINDOW_ADJUST)
                    update.add_int(channel.remote_chanid)
                    update.add_int(32768)
                    transport._send_user_message(update)
                hello = receive_message(channel)
                received.append(hello)
                hello_received.set()
                assert hello.endswith(DELIM), hello
                assert etree.fromstring(hello[:-len(DELIM)]).tag == (
                    '{%s}hello' % NS)
                request = receive_message(channel)
                if chunked:
                    assert request.startswith(b'\n#')
                    size, data = request[2:].split(b'\n', 1)
                    request = data[:int(size)]
                else:
                    request = request[:-len(DELIM)]
                request = etree.fromstring(request)
                reply = ('<rpc-reply xmlns="%s" message-id="%s">'
                         '<data><value>ok</value></data></rpc-reply>'
                         % (NS, request.get('message-id'))).encode()
                if chunked:
                    reply = b'\n#%i\n' % len(reply) + reply + b'\n##\n'
                else:
                    reply += DELIM
                channel.sendall(reply)
                release.wait(5)
        except Exception as error:
            errors.append(error)

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    completed = False
    try:
        yield listener.getsockname()[1], credit, received, hello_received
        completed = True
    finally:
        credit.set()
        release.set()
        listener.close()
        thread.join(6)
        assert not thread.is_alive()
        if completed:
            assert not errors, errors


@pytest.mark.parametrize('delayed', [False, True])
@pytest.mark.parametrize('chunked', [False, True])
def test_hello_uses_end_marker_before_negotiated_rpc(delayed, chunked):
    with ssh_server(delayed, chunked) as server:
        port, credit, received, hello_received = server
        connection = manager.connect_ssh(
            host='127.0.0.1', port=port, username='test', password='test',
            hostkey_verify=False, allow_agent=False, look_for_keys=False,
            timeout=2, manager_params={'timeout': 2})
        try:
            assert connection.session_id == '42'
            credit.set()
            assert hello_received.wait(2)
            assert received[0].endswith(DELIM)
            reply = connection.get()
            assert reply.ok
            assert reply.data_ele.find('{%s}value' % NS).text == 'ok'
            assert len(received) == 1
            assert received[0].endswith(DELIM)
        finally:
            connection._session.close()
