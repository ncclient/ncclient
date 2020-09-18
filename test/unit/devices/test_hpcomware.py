import unittest
from ncclient.devices.hpcomware import *
from ncclient.xml_ import *


class TestHpcomwareDevice(unittest.TestCase):

    def setUp(self):
        self.obj = HpcomwareDeviceHandler({'name': 'hpcomware'})

    def test_get_xml_base_namespace_dict(self):
        expected = {None: BASE_NS_1_0}
        self.assertDictEqual(expected, self.obj.get_xml_base_namespace_dict())

    def test_get_xml_extra_prefix_kwargs(self):
        expected = {'nsmap': {'data': 'http://www.hp.com/netconf/data:1.0',
                              'config': 'http://www.hp.com/netconf/config:1.0',
                              None: 'urn:ietf:params:xml:ns:netconf:base:1.0'}}
        self.assertDictEqual(expected, self.obj.get_xml_extra_prefix_kwargs())

    def test_add_additional_operations(self):
        expected = dict()
        expected['cli_display'] = DisplayCommand
        expected['cli_config'] = ConfigCommand
        expected['action'] = Action
        expected['save'] = Save
        expected['rollback'] = Rollback
        self.assertDictEqual(expected, self.obj.add_additional_operations())
