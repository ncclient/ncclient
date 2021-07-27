from ncclient.operations.lock import *
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


class TestLock(unittest.TestCase):

    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'junos'})

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.RPC._request')
    def test_lock_default_param(self, mock_request, mock_session):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Lock(session, self.device_handler, raise_mode=RaiseMode.ALL)
        obj.request()
        node = new_ele("lock")
        sub_ele(sub_ele(node, "target"), "candidate")
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.RPC._request')
    def test_lock(self, mock_request, mock_session):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Lock(session, self.device_handler, raise_mode=RaiseMode.ALL)
        obj.request(target="running")
        node = new_ele("lock")
        sub_ele(sub_ele(node, "target"), "running")
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.RPC._request')
    def test_unlock_default_param(self, mock_request, mock_session):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Unlock(session, self.device_handler, raise_mode=RaiseMode.ALL)
        obj.request()
        node = new_ele("unlock")
        sub_ele(sub_ele(node, "target"), "candidate")
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.RPC._request')
    def test_unlock(self, mock_request, mock_session):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Unlock(session, self.device_handler, raise_mode=RaiseMode.ALL)
        obj.request(target="running")
        node = new_ele("unlock")
        sub_ele(sub_ele(node, "target"), "running")
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.RPC._request')
    def test_lock_context_enter(self, mock_request, mock_session):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = LockContext(session, self.device_handler, "candidate")
        self.assertEqual(obj.__enter__(), obj)
        node = new_ele("lock")
        sub_ele(sub_ele(node, "target"), "candidate")
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.RPC._request')
    def test_lock_context_exit(self, mock_request, mock_session):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = LockContext(session, self.device_handler, "running")
        self.assertFalse(obj.__exit__())
        node = new_ele("unlock")
        sub_ele(sub_ele(node, "target"), "running")
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)
