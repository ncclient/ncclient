import unittest
from ncclient.devices.default import DefaultDeviceHandler


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
                'urn:liberouter:params:netconf:capability:power-control:1.0',
                'urn:ietf:params:netconf:capability:interleave:1.0',
                'urn:ietf:params:netconf:capability:with-defaults:1.0']

class TestDefaultDevice(unittest.TestCase):

    def setUp(self):
        self.obj = DefaultDeviceHandler()

    def test_get_capabilties(self):
        self.assertEqual(self.obj.get_capabilities(), capabilities)

    def test_get_ssh_subsystem_names(self):
        self.assertEqual(self.obj.get_ssh_subsystem_names(), ["netconf"])

    def test_perform_qualify_check(self):
        self.assertTrue(self.obj.perform_qualify_check())

    def test_handle_raw_dispatch(self):
        self.assertFalse(self.obj.handle_raw_dispatch(None))

    def test_handle_connection_exceptions(self):
        self.assertFalse(self.obj.handle_connection_exceptions(None))


suite = unittest.TestSuite()
unittest.TextTestRunner().run(suite)
