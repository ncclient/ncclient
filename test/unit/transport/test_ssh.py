# -*- coding: utf-8 -*-
import unittest
try:
    from unittest.mock import MagicMock, patch  # Python 3.4 and later
except ImportError:
    from mock import MagicMock, patch
from ncclient.transport.ssh import SSHSession
from ncclient.transport import AuthenticationError, SessionCloseError, NetconfBase
import paramiko
from ncclient.devices.junos import JunosDeviceHandler
import sys

try:
    import selectors
except ImportError:
    import selectors2 as selectors


reply_data = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/12.1X46/junos" attrib1 = "test">
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
</rpc-reply>"""

reply_ok = """<rpc-reply>
    <ok/>
<rpc-reply/>"""

# A buffer of data with two complete messages and an incomplete message
rpc_reply = reply_data + "\n]]>]]>\n" + reply_ok + "\n]]>]]>\n" + reply_ok

reply_ok_chunk = "\n#%d\n%s\n##\n" % (len(reply_ok), reply_ok)

# einarnn: this test message had to be reduced in size as the improved
# 1.1 parsing finds a whole fragment in it, so needed to have less
# data in it than the terminating '>'
reply_ok_partial_chunk = "\n#%d\n%s" % (len(reply_ok), reply_ok[:-1])

# A buffer of data with two complete messages and an incomplete message
rpc_reply11 = "\n#%d\n%s\n#%d\n%s\n##\n%s%s" % (
    30, reply_data[:30], len(reply_data[30:]), reply_data[30:],
    reply_ok_chunk, reply_ok_partial_chunk)


rpc_reply_part_1 = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/12.1X46/junos" attrib1 = "test">
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
]]>]]"""

rpc_reply_part_2 = """>
<rpc-reply>
    <ok/>
<rpc-reply/>"""


class TestSSH(unittest.TestCase):

    def _test_parsemethod(self, mock_dispatch, parsemethod, reply, ok_chunk,
                          expected_messages):
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        if sys.version >= "3.0":
            obj._buffer.write(bytes(reply, "utf-8"))
            remainder = bytes(ok_chunk, "utf-8")
        else:
            obj._buffer.write(reply)
            remainder = ok_chunk
        parsemethod(obj)

        for i in range(0, len(expected_messages)):
            call = mock_dispatch.call_args_list[i][0][0]
            self.assertEqual(call, expected_messages[i])

        self.assertEqual(obj._buffer.getvalue(), remainder)

    @patch('ncclient.transport.ssh.Session._dispatch_message')
    def test_parse(self, mock_dispatch):
        self._test_parsemethod(mock_dispatch, SSHSession._parse, rpc_reply,
                               "\n" + reply_ok, [reply_data])

    @patch('ncclient.transport.ssh.Session._dispatch_message')
    def test_parse11(self, mock_dispatch):
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        if sys.version >= "3.0":
            obj._buffer.write(bytes(rpc_reply11, "utf-8"))
            remainder = bytes(reply_ok_partial_chunk, "utf-8")
        else:
            obj._buffer.write(rpc_reply11)
            remainder = reply_ok_partial_chunk
        obj.parser._parse11()

        expected_messages = [reply_data, reply_ok]
        for i in range(0, len(expected_messages)):
            call = mock_dispatch.call_args_list[i][0][0]
            self.assertEqual(call, expected_messages[i])

        self.assertEqual(obj._buffer.getvalue(), remainder)

    @patch('ncclient.transport.ssh.Session._dispatch_message')
    def test_parse_incomplete_delimiter(self, mock_dispatch):
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        if sys.version >= "3.0":
            b = bytes(rpc_reply_part_1, "utf-8")
            obj._buffer.write(b)
            obj._parse()
            self.assertFalse(mock_dispatch.called)
            b = bytes(rpc_reply_part_2, "utf-8")
            obj._buffer.write(b)
            obj._parse()
            self.assertTrue(mock_dispatch.called)
        else:
            obj._buffer.write(rpc_reply_part_1)
            obj._parse()
            self.assertFalse(mock_dispatch.called)
            obj._buffer.write(rpc_reply_part_2)
            obj._parse()
            self.assertTrue(mock_dispatch.called)

    @patch('paramiko.transport.Transport.auth_publickey')
    @patch('paramiko.agent.AgentSSH.get_keys')
    def test_auth_agent(self, mock_get_key, mock_auth_public_key):
        key = paramiko.PKey(msg="hello")
        mock_get_key.return_value = [key]
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(MagicMock())
        obj._auth('user', 'password', [], True, True)
        self.assertEqual(
            (mock_auth_public_key.call_args_list[0][0][1]).__repr__(),
            key.__repr__())

    @patch('paramiko.transport.Transport.auth_publickey')
    @patch('paramiko.agent.AgentSSH.get_keys')
    def test_auth_agent_exception(self, mock_get_key, mock_auth_public_key):
        key = paramiko.PKey()
        mock_get_key.return_value = [key]
        mock_auth_public_key.side_effect = paramiko.ssh_exception.AuthenticationException
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(MagicMock())
        self.assertRaises(AuthenticationError,
            obj._auth,'user', None, [], True, False)

    @patch('paramiko.transport.Transport.auth_publickey')
    @patch('paramiko.pkey.PKey.from_private_key_file')
    def test_auth_keyfiles(self, mock_get_key, mock_auth_public_key):
        key = paramiko.PKey()
        mock_get_key.return_value = key
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(MagicMock())
        obj._auth('user', 'password', ["key_file_name"], False, True)
        self.assertEqual(
            (mock_auth_public_key.call_args_list[0][0][1]).__repr__(),
            key.__repr__())

    @patch('paramiko.transport.Transport.auth_publickey')
    @patch('paramiko.pkey.PKey.from_private_key_file')
    def test_auth_keyfiles_exception(self, mock_get_key, mock_auth_public_key):
        key = paramiko.PKey()
        mock_get_key.side_effect = paramiko.ssh_exception.PasswordRequiredException
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(MagicMock())
        self.assertRaises(AuthenticationError,
            obj._auth,'user', None, ["key_file_name"], False, True)

    @patch('os.path.isfile')
    @patch('paramiko.transport.Transport.auth_publickey')
    @patch('paramiko.pkey.PKey.from_private_key_file')
    def test_auth_default_keyfiles(self, mock_get_key, mock_auth_public_key,
                                   mock_is_file):
        key = paramiko.PKey()
        mock_get_key.return_value = key
        mock_is_file.return_value = True
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(MagicMock())
        obj._auth('user', 'password', [], False, True)
        self.assertEqual(
            (mock_auth_public_key.call_args_list[0][0][1]).__repr__(),
            key.__repr__())

    @patch('os.path.isfile')
    @patch('paramiko.transport.Transport.auth_publickey')
    @patch('paramiko.pkey.PKey.from_private_key_file')
    def test_auth_default_keyfiles_exception(self, mock_get_key,
                                             mock_auth_public_key, mock_is_file):
        key = paramiko.PKey()
        mock_is_file.return_value = True
        mock_get_key.side_effect = paramiko.ssh_exception.PasswordRequiredException
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(MagicMock())
        self.assertRaises(AuthenticationError,
			              obj._auth,'user', None, [], False, True)

    @patch('paramiko.transport.Transport.auth_password')
    def test_auth_password(self, mock_auth_password):
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(MagicMock())
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
        obj._transport = paramiko.Transport(MagicMock())
        self.assertRaises(AuthenticationError,
            obj._auth, 'user', 'password', [], False, True)

    def test_auth_no_methods_exception(self):
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(MagicMock())
        self.assertRaises(AuthenticationError,
            obj._auth,'user', None, [], False, False)

    @patch('paramiko.transport.Transport.close')
    def test_close(self, mock_close):
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._transport = paramiko.Transport(MagicMock())
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

    @patch('os.path.expanduser')
    @patch('paramiko.hostkeys.HostKeys.load')
    def test_load_host_key_IOError(self, mock_load, mock_os):
        mock_os.return_value = "file_name"
        mock_load.side_effect = IOError
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj.load_known_hosts()
        mock_load.assert_called_with("file_name")

    @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('selectors.DefaultSelector.select')
    @patch('ncclient.transport.ssh.Session._dispatch_error')
    def test_run_receive_py3(self, mock_error, mock_selector, mock_recv, mock_close):
        mock_selector.return_value = True
        mock_recv.return_value = 0
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._channel = paramiko.Channel("c100")
        obj.run()
        self.assertTrue(
            isinstance(
                mock_error.call_args_list[0][0][0],
                SessionCloseError))

    @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
    def test_run_send_py3_10(self):
        self._test_run_send_py3(NetconfBase.BASE_10,
                                lambda msg: msg.encode() + b"]]>]]>")

    @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
    def test_run_send_py3_11(self):
        def chunker(msg):
            encmsg = msg.encode()
            chunks = b"\n#%i\n%b\n##\n" % (len(encmsg), encmsg)
            return chunks
        self._test_run_send_py3(NetconfBase.BASE_11, chunker)

    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('selectors.DefaultSelector.select')
    @patch('ncclient.transport.ssh.Session._dispatch_error')
    def _test_run_send_py3(self, base, chunker, mock_error, mock_selector,
                           mock_send, mock_ready, mock_close):
        mock_selector.return_value = False
        mock_ready.return_value = True
        mock_send.return_value = -1
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._channel = paramiko.Channel("c100")
        msg = "naïve garçon"
        obj._q.put(msg)
        obj._base = base
        obj.run()
        self.assertEqual(mock_send.call_args_list[0][0][0], chunker(msg))
        self.assertTrue(
            isinstance(
                mock_error.call_args_list[0][0][0],
                SessionCloseError))

    @unittest.skipIf(sys.version_info.major >= 3, "test not supported >= Python3")
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('selectors2.DefaultSelector')
    @patch('ncclient.transport.ssh.Session._dispatch_error')
    def test_run_receive_py2(self, mock_error, mock_selector, mock_recv, mock_close):
        mock_selector.select.return_value = True
        mock_recv.return_value = 0
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._channel = paramiko.Channel("c100")
        obj.run()
        self.assertTrue(
            isinstance(
                mock_error.call_args_list[0][0][0],
                SessionCloseError))

    @unittest.skip("test currently non-functional")
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('selectors2.DefaultSelector')
    @patch('ncclient.transport.ssh.Session._dispatch_error')
    def test_run_send_py2(self, mock_error, mock_selector, mock_send, mock_ready, mock_close):
        mock_selector.select.return_value = False
        mock_ready.return_value = True
        mock_send.return_value = -1
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj = SSHSession(device_handler)
        obj._channel = paramiko.Channel("c100")
        obj._q.put("rpc")
        obj.run()
        self.assertEqual(mock_send.call_args_list[0][0][0], "rpc]]>]]>")
        self.assertTrue(
            isinstance(
                mock_error.call_args_list[0][0][0],
                SessionCloseError))
