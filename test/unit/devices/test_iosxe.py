import unittest
from ncclient.devices.iosxe import *


class TestIosxeDevice(unittest.TestCase):
    
    def setUp(self):
        self.obj = IosxeDeviceHandler({'name': 'iosxe'})

    def test_add_additional_operations(self):
        expected = {'save_config': SaveConfig}
        self.assertDictEqual(expected, self.obj.add_additional_operations())

    def test_add_additional_ssh_connect_params(self):
        expected = dict()
        expected["unknown_host_cb"] = iosxe_unknown_host_cb
        actual = dict()
        self.obj.add_additional_ssh_connect_params(actual)
        self.assertDictEqual(expected, actual)

    def test_csr_unknown_host_cb(self):
        self.assertTrue(iosxe_unknown_host_cb('host', 'fingerprint'))
