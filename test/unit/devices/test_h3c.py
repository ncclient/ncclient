import unittest
from ncclient.devices.h3c import *


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
                'urn:ietf:params:netconf:capability:with-defaults:1.0']


class TestH3cDevice(unittest.TestCase):

    def setUp(self):
        self.obj = H3cDeviceHandler({'name': 'h3c'})

    def test_add_additional_operations(self):
        expected = dict()
        expected['get_bulk'] = GetBulk
        expected['get_bulk_config'] = GetBulkConfig
        expected['cli'] = CLI
        expected['action'] = Action
        expected['save'] = Save
        expected['load'] = Load
        expected['rollback'] = Rollback
        self.assertDictEqual(expected, self.obj.add_additional_operations())

    def test_get_capabilities(self):
        self.assertListEqual(capabilities, self.obj.get_capabilities())

    def test_get_xml_extra_prefix_kwargs(self):
        expected = dict()
        expected['nsmap'] = self.obj.get_xml_base_namespace_dict()
        self.assertDictEqual(expected, self.obj.get_xml_extra_prefix_kwargs())

    def test_perform_qualify_check(self):
        self.assertFalse(self.obj.perform_qualify_check())
