import unittest
from xml.etree import ElementTree

try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient import manager
import ncclient.transport
from ncclient.operations.third_party.sros.rpc import *
from ncclient.operations import RaiseMode


class TestRPC(unittest.TestCase):
    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'sros'})

    @patch('ncclient.operations.third_party.sros.rpc.RPC._request')
    def test_MdCliRawCommand(self, mock_request):
        mock_request.return_value = 'sros'
        expected = 'sros'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = MdCliRawCommand(session, self.device_handler)
        command = 'show version'
        actual = obj.request(command=command)
        self.assertEqual(expected, actual)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.sros.rpc.RPC._request')
    @patch('ncclient.operations.third_party.sros.rpc.RPC._assert')
    def test_commit(self, mock_assert, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'sros'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = Commit(session, device_handler, raise_mode=RaiseMode.ALL)

        obj.request(confirmed=True, comment="This is a comment", timeout="50")

        node = new_ele("commit")
        sub_ele(node, "comment",
                attrs={'xmlns': "urn:nokia.com:sros:ns:yang:sr:ietf-netconf-augments"}).text = "This is a comment"
        sub_ele(node, "confirmed")
        sub_ele(node, "confirm-timeout").text = "50"

        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)

        self.assertEqual(call, xml)
