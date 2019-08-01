import unittest
from mock import patch, MagicMock
from ncclient import manager
from ncclient.devices.junos import JunosDeviceHandler
import logging


class TestManager(unittest.TestCase):

    @patch('ncclient.transport.SSHSession')
    def test_ssh(self, mock_ssh):
        m = MagicMock()
        mock_ssh.return_value = m
        conn = self._mock_manager()
        m.connect.assert_called_once_with(host='10.10.10.10',
                                          port=22,
                                          username='user',
                                          password='password',
                                          hostkey_verify=False, allow_agent=False,
                                          timeout=3)
        self.assertEqual(conn._session, m)
        self.assertEqual(conn._timeout, 10)

    @patch('ncclient.manager.connect_ssh')
    def test_connect_ssh(self, mock_ssh):
        manager.connect(host='host')
        mock_ssh.assert_called_once_with(host='host')

    @patch('ncclient.manager.connect_ssh')
    def test_connect_ssh_with_hostkey_ed25519(self, mock_ssh):
        hostkey = 'AAAAC3NzaC1lZDI1NTE5AAAAIIiHpGSf8fla6tCwLpwshvMGmUK+B/0v5CsRu+5v4uT7'
        manager.connect(host='host', hostkey=hostkey)
        mock_ssh.assert_called_once_with(host='host', hostkey=hostkey)

    @patch('ncclient.manager.connect_ssh')
    def test_connect_ssh_with_hostkey_ecdsa(self, mock_ssh):
        hostkey = 'AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBFJV9xLkuntH3Ry0GmK4FjYlW+01Ik4j/gbW+i3yIx+YEkF0B3iM7kiyDPqvmOPuVGfW+gq5oQzzdvHKspNkw70='
        manager.connect(host='host', hostkey=hostkey)
        mock_ssh.assert_called_once_with(host='host', hostkey=hostkey)

    @patch('ncclient.manager.connect_ssh')
    def test_connect_ssh_with_hostkey_rsa(self, mock_ssh):
        hostkey = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQDfEAdDrz3l8+PF510ivzWyX/pjpn3Cp6UgjJOinXz82e1LTURZhKwm8blcP8aWe8Uri65Roe6Q/H1WMaR3jFJj4UW2EZY5N+M4esPhoP/APOnDu2XNKy9AK9yD/Bu64TYgkIPQ/6FHdotcQdYTAJ+ac+YfJMp5mhVPnRIh4rlF08a0/tDHzLJVMEoXzp5nfVHcA4W3+5RRhklbct10U0jxHmG8Db9XbKiEbhWs/UMy59UpJ+zr7zLUYPRntgqqkpCyyfeHFNK1P6m3FmyT06QekOioCFmY05y65dkjAwBlaO1RKj1X1lgCirRWu4vxYBo9ewIGPZtuzeyp7jnl7kGV'
        manager.connect(host='host', hostkey=hostkey)
        mock_ssh.assert_called_once_with(host='host', hostkey=hostkey)

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

    @patch('paramiko.proxy.ProxyCommand')
    @patch('paramiko.Transport')
    @patch('ncclient.transport.ssh.hexlify')
    @patch('ncclient.transport.ssh.Session._post_connect')
    def test_connect_with_ssh_config(self, mock_session, mock_hex, mock_trans, mock_proxy):
        log = logging.getLogger('TestManager.test_connect_with_ssh_config')
        ssh_config_path = 'test/unit/ssh_config'

        conn = manager.connect(host='fake_host',
                                    port=830,
                                    username='user',
                                    password='password',
                                    hostkey_verify=False,
                                    allow_agent=False,
                                    ssh_config=ssh_config_path)

        log.debug(mock_proxy.call_args[0][0])
        self.assertEqual(mock_proxy.called, 1)
        mock_proxy.assert_called_with('ssh -W 10.0.0.1:830 jumphost.domain.com')

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
                                    timeout=3,
                                    hostkey_verify=False,
                                    device_params={'local': True, 'name': 'junos'},
                                    manager_params={'timeout': 10})
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

    def test_make_device_handler_provided_handler(self):
        device_handler = manager.make_device_handler(
            {'handler': JunosDeviceHandler})
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

    @patch('ncclient.manager.Manager.HUGE_TREE_DEFAULT')
    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.rpc.RPC')
    def test_manager_huge_node(self, mock_rpc, mock_session, default_value):

        # Set default value to True only in this test through the default_value mock
        default_value = True

        # true should propagate all the way to the RPC
        conn = self._mock_manager()
        self.assertTrue(conn.huge_tree)
        conn.execute(mock_rpc)
        mock_rpc.assert_called_once()
        self.assertTrue(mock_rpc.call_args[1]['huge_tree'])

        # false should propagate all the way to the RPC
        conn.huge_tree = False
        self.assertFalse(conn.huge_tree)
        mock_rpc.reset_mock()
        conn.execute(mock_rpc)
        mock_rpc.assert_called_once()
        self.assertFalse(mock_rpc.call_args[1]['huge_tree'])

    def _mock_manager(self):
        conn = manager.connect(host='10.10.10.10',
                                    port=22,
                                    username='user',
                                    password='password',
                                    timeout=3,
                                    hostkey_verify=False, allow_agent=False,
                                    device_params={'name': 'junos'},
                                    manager_params={'timeout': 10})
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
                                    device_params={'name': 'junos'},
                                    hostkey_verify=False, allow_agent=False)
        return conn


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestManager)
    unittest.TextTestRunner(verbosity=2).run(suite)
