import unittest
from xml.etree import ElementTree
from ncclient.operations.util import *
from mock import MagicMock

xml = """<filter type="xpath">
        <configuration>
            <system>
                <services/>
            </system>
        </configuration>
    </filter>"""


class TestUtils(unittest.TestCase):

    def test_one_of_1(self):
        self.assertEqual(one_of(None, 10, None), None)

    def test_one_of_2(self):
        self.assertRaises(OperationError,
            one_of, None, 10, 10)

    def test_one_of_3(self):
        self.assertRaises(OperationError,
            one_of, None, None)

    def test_datastore_url(self):
        node = new_ele("target")
        sub_ele(node, "candidate")
        result = ElementTree.tostring(
            datastore_or_url(
                "target",
                "candidate"))
        self.assertEqual(result, ElementTree.tostring(node))

    def test_datastore_url_2(self):
        node = new_ele("web")
        sub_ele(node, "url").text = "http://juniper.net"
        result = ElementTree.tostring(
            datastore_or_url(
                "web",
                "http://juniper.net",
                capcheck=MagicMock()))
        self.assertEqual(result, ElementTree.tostring(node))

    def test_datastore_url_3(self):
        node = new_ele("web")
        result = ElementTree.tostring(
            datastore_or_url(
                "web",
                "http://juniper.net"))
        self.assertEqual(result, ElementTree.tostring(node))

    def test_build_filter(self):
        reply = build_filter(xml)
        call = ElementTree.tostring(reply)
        self.assertEqual(call, ElementTree.tostring(to_ele(xml)))

    def test_build_filter_2(self):
        criteria = "configuration/system"
        filter = ("xpath", criteria)
        reply = build_filter(filter)
        call = ElementTree.tostring(reply)
        node = new_ele("filter", type="xpath")
        node.attrib["select"] = criteria
        self.assertEqual(call, ElementTree.tostring(node))

    def test_build_filter_3(self):
        criteria =  """<configuration>
            <system>
                <services/>
            </system>
        </configuration>"""
        filter = ("subtree", criteria)
        reply = build_filter(filter, capcheck="cap")
        call = ElementTree.tostring(reply)
        node = new_ele("filter", type="subtree")
        node.append(to_ele(criteria))
        self.assertEqual(call, ElementTree.tostring(node))

    def test_build_filter_4(self):
        criteria =  """<configuration>
            <system>
                <services/>
            </system>
        </configuration>"""
        filter = ("text", criteria)
        self.assertRaises(OperationError,
            build_filter, filter, capcheck="cap")
