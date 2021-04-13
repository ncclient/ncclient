import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient import manager
import ncclient.transport
from ncclient.operations.third_party.hpcomware.rpc import *


class TestRPC(unittest.TestCase):
    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'hpcomware'})
    
    @patch('ncclient.operations.third_party.hpcomware.rpc.RPC._request')
    def test_displayCommand(self, mock_request):
        mock_request.return_value = 'hpcomware'
        expected = 'hpcomware'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = DisplayCommand(session, self.device_handler)
        cmds = 'show devices-name'
        actual = obj.request(cmds=cmds)
        self.assertEqual(expected, actual)

        commands = [cmd for cmd in cmds]
        actual = obj.request(cmds=commands)
        self.assertEqual(expected, actual)

    @patch('ncclient.operations.third_party.hpcomware.rpc.RPC._request')
    def test_configCommand(self, mock_request):
        mock_request.return_value = 'hpcomware'
        expected = 'hpcomware'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = ConfigCommand(session, self.device_handler)
        cmds = 'show devices-name'
        actual = obj.request(cmds=cmds)
        self.assertEqual(expected, actual)

        commands = [cmd for cmd in cmds]
        actual = obj.request(cmds=commands)
        self.assertEqual(expected, actual)

    @patch('ncclient.operations.third_party.hpcomware.rpc.RPC._request')
    def test_action(self, mock_request):
        mock_request.return_value = 'hpcomware'
        expected = 'hpcomware'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Action(session, self.device_handler)
        action = '<get>devices-name</get>'
        actual = obj.request(action=action)
        self.assertEqual(expected, actual)

    @patch('ncclient.operations.third_party.hpcomware.rpc.RPC._request')
    def test_save(self, mock_request):
        mock_request.return_value = 'hpcomware'
        expected = 'hpcomware'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Save(session, self.device_handler)
        actual = obj.request()
        self.assertEqual(expected, actual)

        filename = 'devices-name'
        actual = obj.request(filename=filename)
        self.assertEqual(expected, actual)

    @patch('ncclient.operations.third_party.hpcomware.rpc.RPC._request')
    def test_rollback(self, mock_request):
        mock_request.return_value = 'hpcomware'
        expected = 'hpcomware'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Rollback(session, self.device_handler)
        actual = obj.request()
        self.assertEqual(expected, actual)

        filename = 'devices-name'
        actual = obj.request(filename=filename)
        self.assertEqual(expected, actual)
