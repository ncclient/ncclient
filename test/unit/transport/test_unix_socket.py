
import sys
import unittest
import socket
from ncclient.devices.junos import JunosDeviceHandler

try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call

# only import on non-Windows platforms
if sys.platform != 'win32':
    from ncclient.transport.errors import UnixSocketError
    from ncclient.transport.unixSocket import UnixSocketSession

PATH = '/tmp/test_socket.sock'

class TestUnixSocket(unittest.TestCase):

    @unittest.skipIf(sys.platform.startswith('win'), "Skipping on Windows")
    @patch('socket.socket.close')
    def test_close_UnixSocket(self, mock_sock_close_fn):
        session = UnixSocketSession(MagicMock())
        session._socket = socket.socket()
        session._connected = True
        session.close()
        mock_sock_close_fn.assert_called_once_with()
        self.assertFalse(session.connected)

    @unittest.skipIf(sys.platform.startswith('win'), "Skipping on Windows")
    @patch('socket.socket')
    @patch('ncclient.transport.Session._post_connect')
    def test_connect_UnixSocket(self, mock_post_connect, mock_socket):
        session = UnixSocketSession(MagicMock())
        session.connect(path=PATH)
        self.assertTrue(session.connected)
