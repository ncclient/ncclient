import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient import manager
import ncclient.transport
from ncclient.operations.third_party.alu.rpc import *


class TestRPC(unittest.TestCase):
    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'alu'})
    
    @patch('ncclient.operations.third_party.alu.rpc.RPC._request')
    def test_showCLI(self, mock_request):
        mock_request.return_value = 'alu'
        expected = 'alu'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = ShowCLI(session, self.device_handler)
        command = 'show system users'
        actual = obj.request(command=command)
        self.assertEqual(expected, actual)

    @patch('ncclient.operations.third_party.alu.rpc.RPC._request')
    def test_getConfiguration(self, mock_request):
        mock_request.return_value = 'alu'
        expected = 'alu'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetConfiguration(session, self.device_handler)
        content = 'xml'
        actual = obj.request(content=content)
        self.assertEqual(expected, actual)

        filter = '<get>device-name</get>'
        actual = obj.request(content=content, filter=filter)
        self.assertEqual(expected, actual)

        content = 'cli'
        actual = obj.request(content=content, filter=filter)
        self.assertEqual(expected, actual)
        
        detail = True
        actual = obj.request(content=content, filter=filter, detail=detail)
        self.assertEqual(expected, actual)
        
        content = ''
        actual = obj.request(content=content, filter=filter, detail=detail)
        self.assertEqual(expected, actual)
        
    @patch('ncclient.operations.third_party.alu.rpc.RPC._request')
    def test_loadConfiguration(self, mock_request):
        mock_request.return_value = 'alu'
        expected = 'alu'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = LoadConfiguration(session, self.device_handler)
        default_operation = ''
        format = 'xml'
        actual = obj.request(format=format, default_operation=default_operation)
        self.assertEqual(expected, actual)

        default_operation = 'get'
        actual=obj.request(format=format, default_operation=default_operation)
        self.assertEqual(expected, actual)

        config = new_ele('device-name')
        actual=obj.request(format=format, default_operation=default_operation, config=config)
        self.assertEqual(expected, actual)

        config = 'device-name'
        format = 'cli'
        actual=obj.request(format=format, default_operation=default_operation, config=config)
        self.assertEqual(expected, actual)
        
        default_operation = ''
        actual=obj.request(format=format, default_operation=default_operation, config=config)
        self.assertEqual(expected, actual)
