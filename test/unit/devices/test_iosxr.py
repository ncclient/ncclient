import unittest
from ncclient.devices.iosxr import *


class TestIosxrDevice(unittest.TestCase):
    
    def setUp(self):
        self.obj = IosxrDeviceHandler({'name': 'iosxe'})

    def test_add_additional_ssh_connect_params(self):
        expected = dict()
        expected["unknown_host_cb"] = iosxr_unknown_host_cb
        actual = dict()
        self.obj.add_additional_ssh_connect_params(actual)
        self.assertDictEqual(expected, actual)

    def test_perform_qualify_check(self):
        self.assertFalse(self.obj.perform_qualify_check())

    def test_csr_unknown_host_cb(self):
        self.assertTrue(iosxr_unknown_host_cb('host', 'fingerprint'))
