from ncclient.operations.edit import *
import unittest
from mock import patch, MagicMock
from ncclient import manager
import ncclient.manager
import ncclient.transport
from ncclient.xml_ import *
from ncclient.operations import RaiseMode
from xml.etree import ElementTree
from ncclient.operations.errors import MissingCapabilityError
import copy


class TestEdit(unittest.TestCase):

    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'junos'})

    @patch('ncclient.operations.edit.RPC._request')
    def test_edit_config(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = EditConfig(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        root = new_ele('config')
        configuration = sub_ele(root, 'configuration')
        system = sub_ele(configuration, 'system')
        location = sub_ele(system, 'location')
        sub_ele(location, 'building').text = "Main Campus, A"
        sub_ele(location, 'floor').text = "5"
        sub_ele(location, 'rack').text = "27"
        obj.request(copy.deepcopy(root))
        node = new_ele("edit-config")
        node.append(util.datastore_or_url("target", "candidate"))
        node.append(validated_element(root, ("config", qualify("config"))))
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.edit.RPC._request')
    def test_edit_config_2(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = [":rollback-on-error", ":validate"]
        obj = EditConfig(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        root = """
            system {
                host-name foo-bar;
            }
            """
        obj.request(copy.deepcopy(root), format="text", target="running", error_option="rollback-on-error",
                    default_operation="default", test_option="test")
        node = new_ele("edit-config")
        node.append(util.datastore_or_url("target", "running"))
        sub_ele(node, "default-operation").text = "default"
        sub_ele(node, "test-option").text = "test"
        sub_ele(node, "error-option").text = "rollback-on-error"
        config_text = sub_ele(node, "config-text")
        sub_ele(config_text, "configuration-text").text = root
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.RPC._request')
    def test_delete_config(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = DeleteConfig(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        obj.request("candidate")
        node = new_ele("delete-config")
        node.append(util.datastore_or_url("target", "candidate"))
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.RPC._request')
    def test_copy_config(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = CopyConfig(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        obj.request("candidate", "running")
        node = new_ele("copy-config")
        node.append(util.datastore_or_url("target", "running"))
        node.append(util.datastore_or_url("source", "candidate"))
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.RPC._request')
    def test_copy_config_2(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = CopyConfig(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        source = new_ele('source')
        config = sub_ele(source, 'config')
        configuration = sub_ele(config, 'configuration')
        system = sub_ele(configuration, 'system')
        location = sub_ele(system, 'location')
        sub_ele(location, 'building').text = "Main Campus, A"
        sub_ele(location, 'floor').text = "5"
        sub_ele(location, 'rack').text = "27"
        obj.request(copy.deepcopy(source), "candidate")
        node = new_ele("copy-config")
        node.append(util.datastore_or_url("target", "candidate"))
        node.append(validated_element(source, ("source", qualify("source"))))
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.RPC._request')
    def test_validate_config(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = [':validate']
        obj = Validate(session, self.device_handler, raise_mode=RaiseMode.ALL)
        cfg_data = new_ele("config")
        sub_ele(cfg_data, "data")
        obj.request(cfg_data)
        node = new_ele("validate")
        src = sub_ele(node, "source")
        cfg = sub_ele(src, "config")
        sub_ele(cfg, "data")
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.RPC._request')
    def test_validate_datastore(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = [':validate']
        obj = Validate(session, self.device_handler, raise_mode=RaiseMode.ALL)
        obj.request("candidate")
        node = new_ele("validate")
        src = sub_ele(node, "source")
        sub_ele(src, "candidate")
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.RPC._request')
    def test_commit(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = [':candidate', ":confirmed-commit"]
        obj = Commit(session, self.device_handler, raise_mode=RaiseMode.ALL)
        obj.request(confirmed=True, timeout="0")
        node = new_ele("commit")
        sub_ele(node, "confirmed")
        sub_ele(node, "confirm-timeout").text = "0"
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.RPC._request')
    def test_commit_exception(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = [':candidate']
        obj = Commit(session, self.device_handler, raise_mode=RaiseMode.ALL)
        self.assertRaises(MissingCapabilityError,
            obj.request, confirmed=True, timeout="0")

    @patch('ncclient.operations.RPC._request')
    def test_discard_changes(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = [':candidate', ":confirmed-commit"]
        obj = DiscardChanges(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        obj.request()
        node = new_ele("discard-changes")
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.RPC._request')
    def test_cancel_commit(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = [':candidate', ":confirmed-commit"]
        obj = CancelCommit(session, self.device_handler, raise_mode=RaiseMode.ALL)
        obj.request(persist_id="foo")
        node = new_ele("cancel-commit")
        sub_ele(node, "persist-id").text = "foo"
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)
