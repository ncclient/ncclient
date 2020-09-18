import unittest
from ncclient.devices.huaweiyang import *


class TestHuaweiyangDevice(unittest.TestCase):

    def setUp(self):
        self.obj = HuaweiyangDeviceHandler({'name': 'huaweiyang'})

    def test_get_capabilities(self):
        expected = ['urn:ietf:params:netconf:base:1.0', 'urn:ietf:params:netconf:base:1.1']
        self.assertListEqual(expected, self.obj.get_capabilities())

    def test_get_xml_base_namespace_dict(self):
        expected = {None: BASE_NS_1_0}
        self.assertDictEqual(expected, self.obj.get_xml_base_namespace_dict())

    def test_get_xml_extra_prefix_kwargs(self):
        expected = dict()
        expected['nsmap'] = self.obj.get_xml_base_namespace_dict()
        self.assertDictEqual(expected, self.obj.get_xml_extra_prefix_kwargs())
