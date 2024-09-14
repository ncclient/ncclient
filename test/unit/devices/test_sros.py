import unittest

from ncclient.devices.sros import SrosDeviceHandler, ConfigMode
from ncclient.xml_ import to_ele, to_xml, BASE_NS_1_0
from ncclient.operations.third_party.sros.rpc import MdCliRawCommand, Commit

capabilities = ['urn:ietf:params:netconf:base:1.0',
                'urn:ietf:params:netconf:base:1.1',
                'urn:ietf:params:netconf:capability:writable-running:1.0',
                'urn:ietf:params:netconf:capability:candidate:1.0',
                'urn:ietf:params:netconf:capability:confirmed-commit:1.0',
                'urn:ietf:params:netconf:capability:rollback-on-error:1.0',
                'urn:ietf:params:netconf:capability:startup:1.0',
                'urn:ietf:params:netconf:capability:url:1.0?scheme=http,ftp,file,https,sftp',
                'urn:ietf:params:netconf:capability:validate:1.0',
                'urn:ietf:params:netconf:capability:xpath:1.0',
                'urn:ietf:params:netconf:capability:notification:1.0',
                'urn:ietf:params:netconf:capability:interleave:1.0',
                'urn:ietf:params:netconf:capability:with-defaults:1.0',
                'urn:ietf:params:xml:ns:netconf:base:1.0',
                'urn:ietf:params:xml:ns:yang:1',
                'urn:ietf:params:netconf:capability:confirmed-commit:1.1',
                'urn:ietf:params:netconf:capability:validate:1.1']

xml = """<?xml version="1.0" encoding="UTF-8"?><rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:4db8afe2-fbd9-4c13-abaf-f39ef678f63c">
<results xmlns="urn:nokia.com:sros:ns:yang:sr:oper-global">
<md-cli-output-block>TiMOS-B-20.10.B1-5 both/x86_64 Nokia 7750 SR Copyright (c) 2000-2020 Nokia.

All rights reserved. All use subject to applicable license agreements.

Built on Fri Oct 2 18:11:20 PDT 2020 by builder in /builds/c/2010B/B1-5/panos/main/sros

</md-cli-output-block>
</results>
</rpc-reply>"""

class TestSrosDevice(unittest.TestCase):

    def setUp(self):
        self.device_handler = SrosDeviceHandler({'name': 'sros'})

    def test_add_additional_operations(self):
        expected = {
            'md_cli_raw_command': MdCliRawCommand,
            'commit': Commit,
        }
        self.assertDictEqual(expected, self.device_handler.add_additional_operations())

    def test_transform_reply(self):
        expected = xml
        actual = self.device_handler.transform_reply()
        ele = to_ele(xml)
        self.assertEqual(expected, to_xml(actual(ele)))

    def test_get_capabilities_without_config_mode(self):
        """Test capabilities without 'config_mode' set"""
        self.assertListEqual(capabilities, self.device_handler.get_capabilities())

    def test_get_capabilities_with_config_mode_private(self):
        """Test capabilities when 'config_mode' is set to 'private'"""
        device_handler = SrosDeviceHandler({'name': 'sros', 'config_mode': ConfigMode.PRIVATE})
        expected_capabilities = capabilities + ['urn:nokia.com:nc:pc']
        self.assertListEqual(expected_capabilities, device_handler.get_capabilities())

    def test_get_xml_base_namespace_dict(self):
        expected = {None: BASE_NS_1_0}
        self.assertDictEqual(expected, self.device_handler.get_xml_base_namespace_dict())

    def test_get_xml_extra_prefix_kwargs(self):
        expected = dict()
        expected['nsmap'] = self.device_handler.get_xml_base_namespace_dict()
        self.assertDictEqual(expected, self.device_handler.get_xml_extra_prefix_kwargs())

    def test_perform_qualify_check(self):
        self.assertFalse(self.device_handler.perform_qualify_check())
