import unittest
from ncclient import manager
from ncclient.devices.ericsson import *
from ncclient.operations.rpc import *
from ncclient.capabilities import Capabilities
import ncclient.transport

class TestEricssonDevice(unittest.TestCase):

    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'ericsson'})

    def test_rpc_default(self):
        # It is a switch for user to turn on/off "nc" prefix, the "nc" prefix is disable by default
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = RPC(session, self.device_handler, raise_mode=RaiseMode.ALL, timeout=0)

        expected = """<?xml version="1.0" encoding="UTF-8"?><rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="%s"><get-config><source><running/></source></get-config></rpc>""" % obj.id

        node = new_ele("get-config")
        child = sub_ele(node, "source")
        sub_ele(child, "running")

        rpc_node = obj._wrap(node)
        self.assertEqual(rpc_node, expected)

    def test_rpc_disable_nc_prefix(self):
        # It is a switch for user to turn on/off "nc" prefix
        self.device_handler = manager.make_device_handler({'name': 'ericsson', 'with_ns': False})
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = RPC(session, self.device_handler, raise_mode=RaiseMode.ALL, timeout=0)

        expected = """<?xml version="1.0" encoding="UTF-8"?><rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="%s"><get-config><source><running/></source></get-config></rpc>""" % obj.id

        node = new_ele("get-config")
        child = sub_ele(node, "source")
        sub_ele(child, "running")

        # It is a switch for user to turn on/off "nc" prefix
        rpc_node = obj._wrap(node)
        self.assertEqual(rpc_node, expected)

    def test_rpc_enable_nc_prefix(self):
        # It is a switch for user to turn on/off "nc" prefix
        self.device_handler = manager.make_device_handler({'name': 'ericsson', 'with_ns': True})
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = RPC(session, self.device_handler, raise_mode=RaiseMode.ALL, timeout=0)

        expected = """<?xml version="1.0" encoding="UTF-8"?><nc:rpc xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="%s"><nc:get-config><nc:source><nc:running/></nc:source></nc:get-config></nc:rpc>""" % obj.id

        node = new_ele("get-config")
        child = sub_ele(node, "source")
        sub_ele(child, "running")

        rpc_node = obj._wrap(node)
        self.assertEqual(rpc_node, expected)

    def test_rpc_enable_nc_prefix_exception(self):
        # invalid value in "with_ns"
        self.device_handler = manager.make_device_handler({'name': 'ericsson', 'with_ns': "Invalid_value"})
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = RPC(session, self.device_handler, raise_mode=RaiseMode.ALL, timeout=0)

        node = new_ele("get-config")
        child = sub_ele(node, "source")
        sub_ele(child, "running")

        self.assertRaises(OperationError, obj._wrap, node)

suite = unittest.TestSuite()
unittest.TextTestRunner().run(suite)

