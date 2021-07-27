import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient import manager
import ncclient.transport
from ncclient.operations.third_party.iosxe.rpc import *


class TestRPC(unittest.TestCase):
    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'iosxe'})
    
    @patch('ncclient.operations.third_party.iosxe.rpc.RPC._request')
    def test_saveConfig(self, mock_request):
        mock_request.return_value = 'iosxe'
        expected = 'iosxe'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = SaveConfig(session, self.device_handler)
        actual = obj.request()
        self.assertEqual(expected, actual)
