import unittest
from mock import patch
from ncclient.transport.ssh import *
from ncclient.devices.junos import JunosDeviceHandler
import sys

rpc_reply = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/12.1X46/junos" attrib1 = "test">
    <software-information>
        <host-name>R1</host-name>
        <product-model>firefly-perimeter</product-model>
        <product-name>firefly-perimeter</product-name>
        <package-information>
            <name>junos</name>
            <comment>JUNOS Software Release [12.1X46-D10.2]</comment>
        </package-information>
    </software-information>
    <cli>
        <banner></banner>
    </cli>
</rpc-reply>
]]>]]>
<rpc-reply>
    <ok/>
<rpc-reply/>"""


class TestSSH(unittest.TestCase):

    @patch('ncclient.transport.ssh.Session._dispatch_message')
    def test_parse(self, mock_dispatch):
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        if sys.version >= "3.0":
            b = bytes(rpc_reply, "utf-8")
            obj._buffer.write(b)
            obj._parse()
            dispatched_str = (b[0:509]).strip().decode("utf-8")
            call = mock_dispatch.call_args_list[0][0][0]
            self.assertEqual(call, dispatched_str)
            self.assertEqual(obj._buffer.getvalue(), b[515:])
        else:
            obj._buffer.write(rpc_reply)
            obj._parse()
            dispatched_str = (rpc_reply[0:509]).strip()
            call = mock_dispatch.call_args_list[0][0][0]
            self.assertEqual(call, dispatched_str)
            self.assertEqual(obj._buffer.getvalue(), rpc_reply[515:])

    @patch('paramiko.transport.Transport.auth_publickey')
    @patch('paramiko.agent.AgentSSH.get_keys')
    def test_auth_agent(self, mock_get_key, mock_auth_public_key):
        key = paramiko.PKey(msg="hello")
        mock_get_key.return_value = [key]
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(None)
        obj._auth('user', 'password', [], True, True)
        self.assertEqual(
            (mock_auth_public_key.call_args_list[0][0][1]).__repr__(),
            key.__repr__())

    @patch('paramiko.transport.Transport.auth_publickey')
    @patch('paramiko.pkey.PKey.from_private_key_file')
    def test_auth_keyfiles(self, mock_get_key, mock_auth_public_key):
        key = paramiko.PKey()
        mock_get_key.return_value = key
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(None)
        obj._auth('user', 'password', ["key_file_name"], False, True)
        self.assertEqual(
            (mock_auth_public_key.call_args_list[0][0][1]).__repr__(),
            key.__repr__())

    @patch('paramiko.transport.Transport.auth_password')
    def test_auth_password(self, mock_auth_password):
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(None)
        obj._auth('user', 'password', [], False, True)
        self.assertEqual(
            mock_auth_password.call_args_list[0][0],
            ('user',
             'password'))

    @patch('paramiko.transport.Transport.auth_password')
    def test_auth_exception(self, mock_auth_password):
        mock_auth_password.side_effect = Exception
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(None)
        with self.assertRaises(AuthenticationError):
            obj._auth('user', 'password', [], False, True)

    @patch('paramiko.transport.Transport.close')
    def test_close(self, mock_close):
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(None)
        obj._transport.active = True
        obj._connected = True
        obj.close()
        mock_close.assert_called_once_with()
        self.assertFalse(obj._connected)

    @patch('paramiko.hostkeys.HostKeys.load')
    def test_load_host_key(self, mock_load):
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj.load_known_hosts("file_name")
        mock_load.assert_called_once_with("file_name")

    @patch('os.path.expanduser')
    @patch('paramiko.hostkeys.HostKeys.load')
    def test_load_host_key_2(self, mock_load, mock_os):
        mock_os.return_value = "file_name"
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj.load_known_hosts()
        mock_load.assert_called_once_with("file_name")

    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('ncclient.transport.ssh.select')
    @patch('ncclient.transport.ssh.Session._dispatch_error')
    def test_run_recieve(self, mock_error, mock_select, mock_recv, mock_close):
        mock_select.return_value = True, None, None
        mock_recv.return_value = 0
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._channel = paramiko.Channel("c100")
        obj.run()
        self.assertTrue(
            isinstance(
                mock_error.call_args_list[0][0][0],
                SessionCloseError))

    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('ncclient.transport.ssh.Session._dispatch_error')
    def test_run_send(self, mock_error, mock_send, mock_ready, mock_close):
        mock_ready.return_value = True
        mock_send.return_value = -1
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._channel = paramiko.Channel("c100")
        obj._q.put("rpc")
        obj.run()
        self.assertEqual(mock_send.call_args_list[0][0][0], "rpc")
        self.assertTrue(
            isinstance(
                mock_error.call_args_list[0][0][0],
                SessionCloseError))
