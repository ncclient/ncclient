import unittest
from ncclient.devices.alu import *
from ncclient.xml_ import *
import re


xml = """<rpc-reply xmlns:junos="http://xml.alu.net/alu/12.1x46/alu">
<routing-engin>
<name>reX</name>
<commit-success/>
<!-- This is a comment -->
</routing-engin>
<ok/>
</rpc-reply>"""


class TestAluDevice(unittest.TestCase):
    
    def setUp(self):
        self.obj = AluDeviceHandler({'name': 'alu'})

    def test_remove_namespaces(self):
        xmlObj = to_ele(xml)
        expected = re.sub(r'<rpc-reply xmlns:junos="http://xml.alu.net/alu/12.1x46/alu">',
                          r'<?xml version="1.0" encoding="UTF-8"?><rpc-reply>', xml)
        self.assertEqual(expected, to_xml(remove_namespaces(xmlObj)))

    def test_get_capabilities(self):
        expected = ["urn:ietf:params:netconf:base:1.0", ]
        self.assertListEqual(expected, self.obj.get_capabilities())

    def test_get_xml_base_namespace_dict(self):
        expected = {None: BASE_NS_1_0}
        self.assertDictEqual(expected, self.obj.get_xml_base_namespace_dict())

    def test_get_xml_extra_prefix_kwargs(self):
        expected = dict()
        expected["nsmap"] = self.obj.get_xml_base_namespace_dict()
        self.assertDictEqual(expected, self.obj.get_xml_extra_prefix_kwargs())

    def test_add_additional_operations(self):
        expected=dict()
        expected["get_configuration"] = GetConfiguration
        expected["show_cli"] = ShowCLI
        expected["load_configuration"] = LoadConfiguration
        self.assertDictEqual(expected, self.obj.add_additional_operations())
    
    def test_transform_reply(self):
        expected = re.sub(r'<rpc-reply xmlns:junos="http://xml.alu.net/alu/12.1x46/alu">',
                          r'<?xml version="1.0" encoding="UTF-8"?><rpc-reply>', xml)
        actual = self.obj.transform_reply()
        xmlObj = to_ele(xml)
        self.assertEqual(expected, to_xml(actual(xmlObj)))
