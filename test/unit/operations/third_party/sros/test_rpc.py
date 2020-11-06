import unittest

import ncclient.transport

from mock import patch
from ncclient import manager
from ncclient._types import Datastore
from ncclient._types import FilterType
from ncclient.namespaces import Nokia
from ncclient.operations.third_party.sros.rpc import *


class TestRPC(unittest.TestCase):
    def setUp(self):
        self.device_handler = manager.make_device_handler(
                {'name': 'sros'})

    @patch('ncclient.operations.third_party.sros.rpc.RPC._request')
    def test_SrosGetData(self, mock_request):
        mock_request.return_value = 'sros'
        expected = 'sros'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = SrosGetData(session, self.device_handler)
        datastore = Datastore.CANDIDATE
        filter_type = FilterType.SUBTREE

        filter_data = '''
        <configure xmlns="%s"><system/></configure>
        ''' % (Nokia.nsmap['conf'])

        filter = (filter_type, filter_data)
        actual = obj.request(datastore=datastore, filter=filter,
                config_filter=True, max_depth=3)
        self.assertEqual(expected, actual)

    @patch('ncclient.operations.third_party.sros.rpc.RPC._request')
    def test_MdCliRawCommand(self, mock_request):
        mock_request.return_value = 'sros'
        expected = 'sros'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = MdCliRawCommand(session, self.device_handler)
        command = 'show version'
        actual = obj.request(command=command)
        self.assertEqual(expected, actual)
