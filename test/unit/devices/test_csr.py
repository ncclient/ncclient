import unittest
from ncclient.devices.csr import *


class TestCsrDevice(unittest.TestCase):
    
    def setUp(self):
        self.obj = CsrDeviceHandler({'name': 'csr'})

    def test_add_additional_ssh_connect_params(self):
        expected = dict()
        expected["unknown_host_cb"] = csr_unknown_host_cb
        actual = dict()
        self.obj.add_additional_ssh_connect_params(actual)
        self.assertDictEqual(expected, actual)

    def test_csr_unknown_host_cb(self):
        self.assertTrue(csr_unknown_host_cb('host', 'fingerprint'))
