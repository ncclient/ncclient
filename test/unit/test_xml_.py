from ncclient import manager
from ncclient.xml_ import *
import unittest
import os
import sys
file_path = os.path.join(os.getcwd(), "test", "unit", "reply1")


class Test_NCElement(unittest.TestCase):

    def test_ncelement_reply_001(self):
        """test parse rpc_reply and string/data_xml"""
        # read in reply1 contents
        with open(file_path, 'r') as f:
            reply = f.read()
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(reply, transform_reply)
        result_str = result.tostring
        if sys.version >= '3':
            result_str = result_str.decode('UTF-8')
        self.assertEqual(str(result), result_str)
        #data_xml != tostring
        self.assertNotEqual(result_str, result.data_xml)

    def test_ncelement_reply_002(self):
        """test parse rpc_reply and xpath"""
        # read in reply1 contents
        with open(file_path, 'r') as f:
            reply = f.read()
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(reply, transform_reply)
        # XPATH checks work
        self.assertEqual(result.xpath("//host-name")[0].text, "R1")
        self.assertEqual(
            result.xpath("/rpc-reply/software-information/host-name")[0].text,
            "R1")
        self.assertEqual(
            result.xpath("software-information/host-name")[0].text,
            "R1")

    def test_ncelement_reply_003(self):
        """test parse rpc_reply and find"""
        # read in reply1 contents
        with open(file_path, 'r') as f:
            reply = f.read()
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(reply, transform_reply)
        # find
        self.assertEqual(result.findtext(".//host-name"), "R1")
        self.assertEqual(result.find(".//host-name").tag, "host-name")
        self.assertEqual(result.find(".//host-name"), result.findall(".//host-name")[0])
        self.assertEqual(result.findall(".//host-name")[0].tag, "host-name")


class TestXML(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.f = open(file_path, 'r')
        cls.reply = cls.f.read()

    def test_ncelement_reply_001(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        self.assertEqual(result.xpath("//name")[0].text, "junos")
        self.assertEqual(result.xpath("//name")[0].tag, "name")
        self.assertEqual(
            result.xpath("//package-information")[0].tag,
            "package-information")

    def test_ncelement_find(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        self.assertEqual(result.find(".//name").tag, "name")
        self.assertEqual(result.find(".//name").text, "junos")

    def test_ncelement_findtext(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        self.assertEqual(result.findtext(".//name"), "junos")

    def test_ncelement_findall(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        self.assertEqual(result.findall(".//name")[0].tag, "name")
        self.assertEqual(result.findall(".//name")[0].text, "junos")

    def test_ncelement_remove_namespace(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        re = result.remove_namespaces(self.reply)
        self.assertEqual(re.tag, "rpc-reply")
        ele = to_ele((result.find(".//name")))
        self.assertEqual(ele.tag, "name")
        self.assertEqual(ele.text, "junos")
        ele = to_ele(self.reply)
        self.assertEqual(ele.tag, "rpc-reply")

    def test_to_ele(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        ele = to_ele((result.find(".//name")))
        self.assertEqual(ele.tag, "name")
        self.assertEqual(ele.text, "junos")
        ele = to_ele(self.reply)
        self.assertEqual(ele.tag, "rpc-reply")

    def test_parse_root(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        tag, attrib = parse_root(result.data_xml)
        self.assertEqual(tag, "rpc-reply")
        self.assertEqual(attrib, {'attrib1': 'test'})

    def test_validated_element_pass(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        result_xml = result.data_xml
        ele = validated_element(
            result_xml, tags=["rpc-reply", "rpc"], attrs=[["attrib1", "attrib2"]])
        self.assertEqual(ele.tag, "rpc-reply")
        ele = validated_element(
            result_xml, attrs=[["attrib1", "attrib2"]])
        self.assertEqual(ele.tag, "rpc-reply")
        ele = validated_element(result_xml)
        self.assertEqual(ele.tag, "rpc-reply")

    def test_validated_element_fail(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        XMLError.message = "Element does not meet requirement"
        result_xml = result.data_xml
        self.assertRaises(XMLError,
            validated_element,
                result_xml, tags=["rpc"], attrs=[["attrib1", "attrib2"]])

    def test_validated_element_fail_2(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        XMLError.message = "Element does not meet requirement"
        result_xml = result.data_xml
        self.assertRaises(XMLError,
            validated_element,
                result_xml,
                tags=[
                    "rpc-reply",
                    "rpc"],
                attrs=[
                    ["attrib1"],
                    ["attrib2"]])

    def test_validated_element_fail_3(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        XMLError.message = "Element does not meet requirement"
        result_xml = result.data_xml
        self.assertRaises(XMLError,
            validated_element, result_xml, tags=["rpc"])

    def test_sub_ele_inherit_parent_namespace(self):
        device_params = {'name': 'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(self.reply, transform_reply)
        ele = new_ele_ns(result.find("./cli").tag, "http://www.xxx.org")
        child = sub_ele(ele, "child")
        sibling = sub_ele(ele, "sibling")
        grandchild = sub_ele(child, "grandchild")
        self.assertEqual(child.tag, "{http://www.xxx.org}child")
        self.assertEqual(sibling.tag, "{http://www.xxx.org}sibling")
        self.assertEqual(grandchild.tag, "{http://www.xxx.org}grandchild")
