from ncclient.operations.third_party.juniper.rpc import *
import unittest
from mock import patch
from ncclient import manager
import ncclient.manager
import ncclient.transport
from ncclient.xml_ import *
from ncclient.operations import RaiseMode
from xml.etree import ElementTree


class TestRPC(unittest.TestCase):

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._request')
    def test_command(self, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'junos'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = Command(session, device_handler, raise_mode=RaiseMode.ALL)
        command = 'show system users'
        format = 'text'
        obj.request(command=command, format=format)
        node = new_ele('command', {'format': format})
        node.text = command
        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(call.tag, node.tag)
        self.assertEqual(call.text, node.text)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._request')
    def test_getconf(self, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'junos'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = GetConfiguration(
            session,
            device_handler,
            raise_mode=RaiseMode.ALL)
        root_filter = new_ele('filter')
        config_filter = sub_ele(root_filter, 'configuration')
        system_filter = sub_ele(config_filter, 'system')
        obj.request(format='xml', filter=system_filter)
        node = new_ele('get-configuration', {'format': 'xml'})
        node.append(system_filter)
        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(call.tag, node.tag)
        self.assertEqual(call.attrib, node.attrib)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._request')
    def test_compare_conf(self, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'junos'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = CompareConfiguration(
            session,
            device_handler,
            raise_mode=RaiseMode.ALL)
        obj.request(rollback=2)
        node = new_ele(
            'get-configuration', {'compare': 'rollback', 'rollback': str(2)})
        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(call.tag, node.tag)
        self.assertEqual(call.attrib, node.attrib)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._request')
    def test_execute_rpc(self, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'junos'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
        rpc = new_ele('get-software-information')
        obj.request(rpc)
        mock_request.assert_called_once_with(rpc)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._request')
    def test_reboot(self, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'junos'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = Reboot(session, device_handler, raise_mode=RaiseMode.ALL)
        obj.request()
        node = new_ele('request-reboot')
        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(call.tag, node.tag)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._request')
    def test_halt(self, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'junos'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = Halt(session, device_handler, raise_mode=RaiseMode.ALL)
        obj.request()
        node = new_ele('request-halt')
        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(call.tag, node.tag)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._request')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._assert')
    def test_commit_confirmed(self, mock_assert, mock_request, mock_session):
        # mock_session.server_capabilities.return_value = [':candidate']
        device_handler = manager.make_device_handler({'name': 'junos'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = Commit(session, device_handler, raise_mode=RaiseMode.ALL)
        obj.request(confirmed=True, comment="message", timeout="50")
        node = new_ele("commit")
        sub_ele(node, "confirmed")
        sub_ele(node, "confirm-timeout").text = "50"
        sub_ele(node, "log").text = "message"
        xml = ElementTree.tostring(node, method='xml')
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call, method='xml')
        self.assertEqual(call, xml)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._request')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._assert')
    def test_commit(self, mock_assert, mock_request, mock_session):
        # mock_session.server_capabilities.return_value = [':candidate']
        device_handler = manager.make_device_handler({'name': 'junos'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = Commit(session, device_handler, raise_mode=RaiseMode.ALL)
        obj.request()
        node = new_ele("commit")
        xml = ElementTree.tostring(node, method='xml')
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call, method='xml')
        self.assertEqual(call, xml)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._request')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._assert')
    def test_commit_at_time(self, mock_assert, mock_request, mock_session):
        # mock_session.server_capabilities.return_value = [':candidate']
        device_handler = manager.make_device_handler({'name': 'junos'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = Commit(session, device_handler, raise_mode=RaiseMode.ALL)
        obj.request(at_time="1111-11-11 00:00:00", synchronize=True)
        node = new_ele("commit")
        sub_ele(node, "at-time").text = "1111-11-11 00:00:00"
        sub_ele(node, "synchronize")
        xml = ElementTree.tostring(node, method='xml')
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call, method='xml')
        self.assertEqual(call, xml)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._request')
    @patch('ncclient.operations.third_party.juniper.rpc.RPC._assert')
    def test_commit_confirmed_at_time(
            self, mock_assert, mock_request, mock_session):
        # mock_session.server_capabilities.return_value = [':candidate']
        device_handler = manager.make_device_handler({'name': 'junos'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = Commit(session, device_handler, raise_mode=RaiseMode.ALL)
        with self.assertRaises(NCClientError):
            obj.request(
                at_time="1111-11-11 00:00:00",
                synchronize=True,
                confirmed=True)
