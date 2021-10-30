import unittest
from ncclient.devices.nexus import *


capabilities = ['urn:ietf:params:xml:ns:netconf:base:1.0',
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


class TestNexusDevice(unittest.TestCase):

    def setUp(self):
        self.obj = NexusDeviceHandler({'name': 'nexus'})

    def test_add_additional_operations(self):
        expected = {'exec_command': ExecCommand}
        self.assertDictEqual(expected, self.obj.add_additional_operations())

    def test_get_capabilities(self):
        self.assertListEqual(capabilities, self.obj.get_capabilities())

    def test_get_xml_base_namespace_dict(self):
        expected = {None: BASE_NS_1_0}
        self.assertDictEqual(expected, self.obj.get_xml_base_namespace_dict())

    def test_get_xml_extra_prefix_kwargs(self):
        temp = {
            'nxos': 'http://www.cisco.com/nxos:1.0',
            'if': 'http://www.cisco.com/nxos:1.0:if_manager',
            'nfcli': 'http://www.cisco.com/nxos:1.0:nfcli',
            'vlan_mgr_cli': 'http://www.cisco.com/nxos:1.0:vlan_mgr_cli'
        }
        temp.update(self.obj.get_xml_base_namespace_dict())
        expected = dict()
        expected['nsmap'] = temp
        self.assertDictEqual(expected, self.obj.get_xml_extra_prefix_kwargs())

    def test_get_ssh_subsystem_names(self):
        expected = ['netconf', 'xmlagent']
        self.assertListEqual(expected, self.obj.get_ssh_subsystem_names())

        expected.insert(0, 'ncclient')
        self.obj = NexusDeviceHandler({'ssh_subsystem_name': 'ncclient'}) 
        self.assertListEqual(expected, self.obj.get_ssh_subsystem_names())
