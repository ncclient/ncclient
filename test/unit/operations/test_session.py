from ncclient.operations.session import *
import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient import manager
import ncclient.manager
import ncclient.transport
from ncclient.xml_ import *
from ncclient.operations import RaiseMode
from xml.etree import ElementTree


class TestSession(unittest.TestCase):

    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'junos'})

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.RPC._request')
    def test_close_session(self, mock_request, mock_session):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = CloseSession(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        obj.request()
        node = new_ele("close-session")
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.RPC._request')
    def test_kill_session(self, mock_request, mock_session):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = KillSession(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        obj.request("100")
        node = new_ele("kill-session")
        sub_ele(node, "session-id").text = "100"
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)
