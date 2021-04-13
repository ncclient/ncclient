import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient import manager
import ncclient.transport
from ncclient.operations.third_party.huawei.rpc import *


class TestRPC(unittest.TestCase):
    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'huawei'})
     
    @patch('ncclient.operations.third_party.huawei.rpc.RPC._request')
    def test_CLI(self, mock_request):
        mock_request.return_value = 'huawei'
        expected = 'huawei'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = CLI(session, self.device_handler)
        command = '<get>devices-name</get>'
        actual = obj.request(command=command)
        self.assertEqual(expected, actual)

    @patch('ncclient.operations.third_party.huawei.rpc.RPC._request')
    def test_action(self, mock_request):
        mock_request.return_value = 'huawei'
        expected = 'huawei'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Action(session, self.device_handler)
        action = '<get>devices-name</get>'
        actual = obj.request(action=action)
        self.assertEqual(expected, actual)

