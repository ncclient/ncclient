import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient import manager
import ncclient.transport
from ncclient.operations.third_party.sros.rpc import *


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
