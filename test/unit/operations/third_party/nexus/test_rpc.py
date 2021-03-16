import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient import manager
import ncclient.transport
from ncclient.operations.third_party.nexus.rpc import *


class TestRPC(unittest.TestCase):
    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'nexus'})
    
    @patch('ncclient.operations.third_party.nexus.rpc.RPC._request')
    def test_execCommand(self, mock_request):
        mock_request.return_value = 'nexus'
        expected = 'nexus'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = ExecCommand(session, self.device_handler)
        cmds = 'show devices-name'
        actual = obj.request(cmds=cmds)
        self.assertEqual(expected, actual)

        commands = [cmd for cmd in cmds]
        actual = obj.request(cmds=commands)
        self.assertEqual(expected, actual)
