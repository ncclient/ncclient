import unittest
from ncclient.devices.iosxe import *
from ncclient.xml_ import new_ele
from ncclient.xml_ import qualify
from ncclient.xml_ import validated_element


CFG_BROKEN = """
<config>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname>tl-einarnn-c8kv</hostname>
  </native>
</config>
"""


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

    def test_iosxe_transform_edit_config(self):
        node = new_ele("edit-config")
        node.append(validated_element(CFG_BROKEN, ("config", qualify("config"))))
        node = self.obj.transform_edit_config(node)
        config_nodes = node.findall('./config')
        self.assertTrue(len(config_nodes) == 0)
