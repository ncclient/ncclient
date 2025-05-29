import unittest
from ncclient.devices.ciena import *
from ncclient.xml_ import *


class TestCienaDevice(unittest.TestCase):
    
    def setUp(self):
        self.obj = CienaDeviceHandler({'name': 'ciena'})

    def test_get_xml_base_namespace_dict(self):
        expected = {None: BASE_NS_1_0}
        self.assertDictEqual(expected, self.obj.get_xml_base_namespace_dict())

    def test_get_xml_extra_prefix_kwargs(self):
        expected = dict()
        expected["nsmap"] = self.obj.get_xml_base_namespace_dict()
        self.assertDictEqual(expected, self.obj.get_xml_extra_prefix_kwargs())
