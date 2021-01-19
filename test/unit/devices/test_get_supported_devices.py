import unittest
from ncclient import devices

class  TestGetSupportedDevices(unittest.TestCase):

    def test_get_supported_devices(self):
        supported_devices = devices.get_supported_devices()
        self.assertEqual(sorted(supported_devices), sorted(('junos',
                                                            'csr',
                                                            'nexus',
                                                            'iosxr',
                                                            'iosxe',
                                                            'huawei',
                                                            'huaweiyang',
                                                            'alu',
                                                            'h3c',
                                                            'hpcomware',
                                                            'sros',
                                                            'default')))

    def test_get_supported_device_labels(self):
        supported_device_labels = devices.get_supported_device_labels()
        self.assertEqual(supported_device_labels, {'junos':'Juniper',
                                                   'csr':'Cisco CSR1000v',
                                                   'nexus':'Cisco Nexus',
                                                   'iosxr':'Cisco IOS XR',
                                                   'iosxe':'Cisco IOS XE',
                                                   'huawei':'Huawei',
                                                   'huaweiyang':'Huawei',
                                                   'alu':'Alcatel Lucent',
                                                   'h3c':'H3C',
                                                   'hpcomware':'HP Comware',
                                                   'sros':'Nokia SR OS',
                                                   'default':'Server or anything not in above'})

