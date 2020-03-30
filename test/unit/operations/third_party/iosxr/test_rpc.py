from ncclient.operations.third_party.juniper.rpc import *
import json
import unittest
from mock import patch
from ncclient import manager
import ncclient.manager
import ncclient.transport
from ncclient.xml_ import *
from ncclient.operations import RaiseMode
from xml.etree import ElementTree


class TestRPC(unittest.TestCase):

    @patch('ncclient.transport.SSHSession')
    @patch('ncclient.operations.third_party.iosxr.rpc.RPC._request')
    def test_execute_rpc(self, mock_request, mock_session):
        device_handler = manager.make_device_handler({'name': 'iosxr'})
        session = ncclient.transport.SSHSession(device_handler)
        obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
        rpc = new_ele('get-software-information')
        obj.request(rpc)
        mock_request.assert_called_once_with(rpc)
