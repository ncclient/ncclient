# Copyright (c) Siemens AG, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ssl
import sys
import unittest
import socket
from unittest.mock import MagicMock, patch, call

try:
    from ssl import PROTOCOL_TLS_CLIENT
    tls_proto = PROTOCOL_TLS_CLIENT
except ImportError:
    from ssl import PROTOCOL_TLS
    tls_proto = PROTOCOL_TLS

from ncclient.transport.errors import TLSError
from ncclient.transport.tls import TLSSession, DEFAULT_TLS_NETCONF_PORT


HOST = '10.10.10.10'
PORT = DEFAULT_TLS_NETCONF_PORT
KEYFILE = 'test/unit/transport/certs/test.key'
CERTFILE_WO_KEY = 'test/unit/transport/certs/test.crt'
CERTFILE_WITH_KEY = 'test/unit/transport/certs/test.pem'


class TestTLS(unittest.TestCase):

    @patch('ssl.SSLContext.wrap_socket')
    @patch('ncclient.transport.Session._post_connect')
    def test_connect_tls_certfile_with_key(self, mock_post_connect, mock_wrap_socket_fn):
        session = TLSSession(MagicMock())
        mock_wrap_socket = MagicMock()
        mock_wrap_socket_fn.return_value = mock_wrap_socket
        session.connect(host=HOST, certfile=CERTFILE_WITH_KEY,
                        protocol=tls_proto)
        mock_wrap_socket.connect.assert_called_once_with(
            (HOST, DEFAULT_TLS_NETCONF_PORT))
        self.assertTrue(session.connected)

    @patch('ssl.SSLContext.wrap_socket')
    @patch('ncclient.transport.Session._post_connect')
    def test_connect_tls_certfile_without_key(self, mock_post_connect, mock_wrap_socket_fn):
        session = TLSSession(MagicMock())
        mock_wrap_socket = MagicMock()
        mock_wrap_socket_fn.return_value = mock_wrap_socket
        session.connect(host=HOST, certfile=CERTFILE_WO_KEY, keyfile=KEYFILE,
                        protocol=tls_proto)
        mock_wrap_socket.connect.assert_called_once_with(
            (HOST, DEFAULT_TLS_NETCONF_PORT))
        self.assertTrue(session.connected)

    @unittest.skipIf(sys.version_info < (3, 6), "test not supported < Python3.6")
    @patch('ssl.SSLContext.wrap_socket')
    @patch('ncclient.transport.Session._post_connect')
    def test_tls_handshake(self, mock_post_connect, mock_wrap_socket_fn):
        session = TLSSession(MagicMock())
        mock_wrap_socket = MagicMock()
        mock_wrap_socket_fn.return_value = mock_wrap_socket
        session.connect(host=HOST, certfile=CERTFILE_WITH_KEY,
                        protocol=tls_proto)
        mock_wrap_socket.do_handshake.assert_called_once()

    @patch('ssl.SSLContext.wrap_socket')
    def test_tls_unsuccessul_handshake(self, mock_wrap_socket_fn):
        session = TLSSession(MagicMock())
        mock_wrap_socket = MagicMock()
        mock_wrap_socket.do_handshake = MagicMock(side_effect=ssl.SSLError)
        mock_wrap_socket_fn.return_value = mock_wrap_socket
        with self.assertRaises(TLSError):
            session.connect(host=HOST, certfile=CERTFILE_WITH_KEY,
                            protocol=tls_proto)

    def test_connect_tls_missing_hostname(self):
        session = TLSSession(MagicMock())
        with self.assertRaises(TLSError):
            session.connect(host=None, certfile=CERTFILE_WITH_KEY,
                            protocol=tls_proto)

    def test_connect_tls_missing_certfile(self):
        session = TLSSession(MagicMock())
        with self.assertRaises(TLSError):
            session.connect(host=HOST, certfile=None,
                            protocol=tls_proto)

    def test_connect_tls_missing_private_key(self):
        session = TLSSession(MagicMock())
        with self.assertRaises(TLSError):
            session.connect(host=HOST, certfile=CERTFILE_WO_KEY,
                            protocol=tls_proto)

    def test_connect_tls_missing_ca_file(self):
        session = TLSSession(MagicMock())
        with self.assertRaises(TLSError):
            # Use arbitrary string to point to non-existing key location.
            session.connect(host=HOST, certfile=CERTFILE_WITH_KEY,
                            ca_certs='-', protocol=tls_proto)

    @patch('socket.socket.close')
    def test_close_tls(self, mock_sock_close_fn):
        session = TLSSession(MagicMock())
        session._socket = socket.socket()
        session._connected = True
        session.close()
        mock_sock_close_fn.assert_called_once_with()
        self.assertFalse(session._connected)
