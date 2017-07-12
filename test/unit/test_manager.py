import unittest
from mock import patch, MagicMock
from ncclient import manager


class TestManager(unittest.TestCase):

    @patch('ncclient.transport.SSHSession')
    def test_ssh(self, mock_ssh):
        m = MagicMock()
        mock_ssh.return_value = m
        conn = self._mock_manager()
        self.assertEqual(conn._session, m)
        self.assertEqual(conn._timeout, 10)

    @patch('ncclient.manager.connect_ssh')
    def test_connect_ssh(self, mock_ssh):
        manager.connect(host='host')
        mock_ssh.assert_called_once_with(host='host')

    @patch('ncclient.manager.connect_ssh')
    def test_connect_outbound_ssh(self, mock_ssh):
        manager.connect(host=None, sock_fd=6)
        mock_ssh.assert_called_once_with(host=None, sock_fd=6)

    @patch('ncclient.manager.connect_ioproc')
    def test_connect_ioproc(self, mock_ssh):
        manager.connect(host='localhost', device_params={'name': 'junos', 
                                                        'local': True})
        mock_ssh.assert_called_once_with(host='localhost', 
                            device_params={'local': True, 'name': 'junos'})

    @patch('socket.socket')
    @patch('paramiko.Transport')
    @patch('ncclient.transport.ssh.hexlify')
    @patch('ncclient.transport.ssh.Session._post_connect')
    def test_ssh2(self, mock_session, mock_hex, mock_trans, mock_socket):
        conn = self._mock_manager()
        self.assertEqual(mock_trans.called, 1)
        self.assertEqual(conn._timeout, 10)
        self.assertEqual(conn._device_handler.device_params, {'name': 'junos'})
        self.assertEqual(
            conn._device_handler.__class__.__name__,
            "JunosDeviceHandler")

    @patch('ncclient.transport.ssh.Session._post_connect')
    @patch('ncclient.transport.third_party.junos.ioproc.IOProc.connect')
    def test_ioproc(self, mock_connect, mock_ioproc):
        conn = manager.connect(host='localhost',
                                    port=22,
                                    username='user',
                                    password='password',
                                    timeout=10,
                                    device_params={'local': True, 'name': 'junos'},
                                    hostkey_verify=False)
        self.assertEqual(mock_connect.called, 1)
        self.assertEqual(conn._timeout, 10)
        self.assertEqual(conn._device_handler.device_params, {'local': True, 'name': 'junos'}) 
        self.assertEqual(
            conn._device_handler.__class__.__name__,
            "JunosDeviceHandler")

    def test_make_device_handler(self):
        device_handler = manager.make_device_handler({'name': 'junos'})
        self.assertEqual(
            device_handler.__class__.__name__,
            "JunosDeviceHandler")

    @patch('ncclient.operations.LockContext')
    def test_manager_locked(self, mock_lock):
        conn = manager.Manager(None, None, timeout=20)
        conn.locked(None)
        mock_lock.assert_called_once_with(None, None, None)

    @patch('socket.socket')
    @patch('paramiko.Transport')
    @patch('ncclient.transport.ssh.hexlify')
    @patch('ncclient.transport.ssh.Session._post_connect')
    def test_manager_client_capability(
            self, mock_session, mock_hex, mock_trans, mock_socket):
        conn = self._mock_manager()
        self.assertEqual(
            conn.client_capabilities,
            conn._session.client_capabilities)

    @patch('socket.socket')
    @patch('paramiko.Transport')
    @patch('ncclient.transport.ssh.hexlify')
    @patch('ncclient.transport.ssh.Session._post_connect')
    def test_manager_server_capability(
            self, mock_session, mock_hex, mock_trans, mock_socket):
        conn = self._mock_manager()
        self.assertEqual(
            conn.server_capabilities,
            conn._session.server_capabilities)

    @patch('socket.socket')
    @patch('paramiko.Transport')
    @patch('ncclient.transport.ssh.hexlify')
    @patch('ncclient.transport.ssh.Session._post_connect')
    def test_manager_channel_id(
            self, mock_session, mock_hex, mock_trans, mock_socket):
        conn = self._mock_manager()
        self.assertEqual(conn.channel_id, conn._session._channel_id)

    @patch('socket.socket')
    @patch('paramiko.Transport')
    @patch('ncclient.transport.ssh.hexlify')
    @patch('ncclient.transport.ssh.Session._post_connect')
    def test_manager_channel_name(
            self, mock_session, mock_hex, mock_trans, mock_socket):
        conn = self._mock_manager()
        self.assertEqual(conn.channel_name, conn._session._channel_name)

    @patch('socket.socket')
    @patch('paramiko.Transport')
    @patch('ncclient.transport.ssh.hexlify')
    @patch('ncclient.transport.ssh.Session._post_connect')
    def test_manager_channel_session_id(
            self, mock_session, mock_hex, mock_trans, mock_socket):
        conn = self._mock_manager()
        self.assertEqual(conn.session_id, conn._session.id)

    @patch('socket.socket')
    @patch('paramiko.Transport')
    @patch('ncclient.transport.ssh.hexlify')
    @patch('ncclient.transport.ssh.Session._post_connect')
    def test_manager_connected(
            self, mock_session, mock_hex, mock_trans, mock_socket):
        conn = self._mock_manager()
        self.assertEqual(conn.connected, True)

    def _mock_manager(self):
        conn = manager.connect(host='10.10.10.10',
                                    port=22,
                                    username='user',
                                    password='password',
                                    timeout=10,
                                    device_params={'name': 'junos'},
                                    hostkey_verify=False, allow_agent=False)
        return conn

    @patch('socket.fromfd')
    @patch('paramiko.Transport')
    @patch('ncclient.transport.ssh.hexlify')
    @patch('ncclient.transport.ssh.Session._post_connect')
    def test_outbound_manager_connected(
            self, mock_session, mock_hex, mock_trans, mock_fromfd):
        conn = self._mock_outbound_manager()
        self.assertEqual(conn.connected, True)

    def _mock_outbound_manager(self):
        conn = manager.connect(host=None,
                                    sock_fd=6,
                                    username='user',
                                    password='password',
                                    timeout=10,
                                    device_params={'name': 'junos'},
                                    hostkey_verify=False, allow_agent=False)
        return conn

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestManager)
    unittest.TextTestRunner(verbosity=2).run(suite)
