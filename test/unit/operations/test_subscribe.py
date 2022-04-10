from ncclient.operations.edit import *
from ncclient.operations.subscribe import *
import unittest
try:
    from unittest.mock import patch, MagicMock  # Python 3.4 and later
except ImportError:
    from mock import patch, MagicMock
from ncclient import manager
import ncclient.manager
import ncclient.transport
from ncclient.xml_ import *
from ncclient.operations import RaiseMode
from xml.etree import ElementTree
from ncclient.operations.errors import MissingCapabilityError
import copy

start_time = "1990-12-31T23:59:60Z"
stop_time = "1996-12-19T16:39:57-08:00"

class TestSubscribe(unittest.TestCase):

    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'junos'})

    @patch('ncclient.operations.edit.RPC._request')
    def test_subscribe_all(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = [":notification"]
        obj = CreateSubscription(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        obj.request()
        node = new_ele_ns("create-subscription", NETCONF_NOTIFICATION_NS)
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.edit.RPC._request')
    def test_subscribe_stream(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = [":notification"]
        obj = CreateSubscription(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        obj.request(filter=None, stream_name="nameofstream")
        node = new_ele_ns("create-subscription", NETCONF_NOTIFICATION_NS)
        sub_ele_ns(node, "stream", NETCONF_NOTIFICATION_NS).text = "nameofstream"
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.edit.RPC._request')
    def test_subscribe_times(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = [":notification"]
        obj = CreateSubscription(
            session,
            self.device_handler,
            raise_mode=RaiseMode.ALL)
        obj.request(filter=None, start_time=start_time, stop_time=stop_time)
        node = new_ele_ns("create-subscription", NETCONF_NOTIFICATION_NS)
        sub_ele_ns(node, "startTime", NETCONF_NOTIFICATION_NS).text = start_time
        sub_ele_ns(node, "stopTime", NETCONF_NOTIFICATION_NS).text = stop_time
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)
