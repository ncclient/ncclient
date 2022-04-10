from ncclient.operations.retrieve import *
import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient import manager
import ncclient.manager
import ncclient.transport
from ncclient.capabilities import Capabilities
from ncclient.xml_ import *
from ncclient.operations import RaiseMode
from ncclient.operations.errors import MissingCapabilityError
from xml.etree import ElementTree
from lxml import etree
import copy
import six


class TestRetrieve(unittest.TestCase):
    def setUp(self):
        self.device_handler = manager.make_device_handler({'name': 'junos'})

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Get(session, self.device_handler, raise_mode=RaiseMode.ALL)
        root_filter = new_ele('filter')
        config_filter = sub_ele(root_filter, 'configuration')
        system_filter = sub_ele(config_filter, 'system')
        sub_ele(system_filter, 'services')
        obj.request(copy.deepcopy(root_filter))
        node = new_ele("get")
        node.append(util.build_filter(root_filter))
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_with_defaults_basic_mode(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = Capabilities([
            "urn:ietf:params:netconf:capability:with-defaults:1.0"
            "?basic-mode=explicit"
        ])
        obj = Get(session, self.device_handler, raise_mode=RaiseMode.ALL)
        obj.request(with_defaults='explicit')

        expected_xml = etree.fromstring(
            '<nc:get xmlns:nc="{base}">'
            '<ns0:with-defaults xmlns:ns0="{defaults}">explicit</ns0:with-defaults>'
            '</nc:get>'.format(
                base=BASE_NS_1_0,
                defaults=NETCONF_WITH_DEFAULTS_NS
            )
        )

        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(etree.tostring(call), etree.tostring(expected_xml))

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_with_defaults_also_supported(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = Capabilities([
            "urn:ietf:params:netconf:capability:with-defaults:1.0"
            "?basic-mode=explicit"
            "&also-supported=report-all,trim"
        ])
        obj = Get(session, self.device_handler, raise_mode=RaiseMode.ALL)
        obj.request(with_defaults='report-all')

        expected_xml = etree.fromstring(
            '<nc:get xmlns:nc="{base}">'
            '<ns0:with-defaults xmlns:ns0="{defaults}">report-all</ns0:with-defaults>'
            '</nc:get>'.format(
                base=BASE_NS_1_0,
                defaults=NETCONF_WITH_DEFAULTS_NS
            )
        )

        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(etree.tostring(call), etree.tostring(expected_xml))

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_with_defaults_not_supported(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = Capabilities([
            "urn:ietf:params:netconf:capability:with-defaults:1.0"
            "?basic-mode=explicit"
            "&also-supported=report-all,trim"
        ])
        obj = Get(session, self.device_handler, raise_mode=RaiseMode.ALL)

        expected_error = (
            "Invalid 'with-defaults' mode 'report-all-tagged'; the server "
            "only supports the following: explicit, report-all, trim"
        )
        six.assertRaisesRegex(
            self,
            WithDefaultsError,
            expected_error,
            obj.request,
            with_defaults='report-all-tagged'
        )

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_with_defaults_missing_capability(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = Capabilities([])
        obj = Get(session, self.device_handler, raise_mode=RaiseMode.ALL)
        self.assertRaises(
            MissingCapabilityError,
            obj.request,
            with_defaults='report-all'
        )

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_config(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetConfig(session, self.device_handler, raise_mode=RaiseMode.ALL)
        source = "candidate"
        obj.request(source)
        node = new_ele("get-config")
        node.append(util.datastore_or_url("source", source))
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_config_with_defaults(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = Capabilities([
            "urn:ietf:params:netconf:capability:with-defaults:1.0"
            "?basic-mode=explicit"
        ])
        obj = GetConfig(session, self.device_handler, raise_mode=RaiseMode.ALL)
        source = 'candidate'
        obj.request(source, with_defaults='explicit')

        expected_xml = etree.fromstring(
            '<nc:get-config xmlns:nc="{base}">'
            '<nc:source><nc:candidate /></nc:source>'
            '<ns0:with-defaults xmlns:ns0="{defaults}">explicit</ns0:with-defaults>'
            '</nc:get-config>'.format(
                base=BASE_NS_1_0,
                defaults=NETCONF_WITH_DEFAULTS_NS
            )
        )

        call = mock_request.call_args_list[0][0][0]
        self.assertEqual(etree.tostring(call), etree.tostring(expected_xml))

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_config_with_defaults_missing_capability(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = Capabilities([])
        obj = GetConfig(session, self.device_handler, raise_mode=RaiseMode.ALL)
        source = 'candidate'
        self.assertRaises(
            MissingCapabilityError,
            obj.request,
            source,
            with_defaults='explicit'
        )

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_schema(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetSchema(session, self.device_handler, raise_mode=RaiseMode.ALL)
        identifier = "foo"
        version = "1.0"
        reqformat = "xsd"
        obj.request(identifier, version, reqformat)
        node = etree.Element(qualify("get-schema", NETCONF_MONITORING_NS))
        id = etree.SubElement(node,
                              qualify("identifier", NETCONF_MONITORING_NS))
        id.text = identifier
        ver = etree.SubElement(node, qualify("version", NETCONF_MONITORING_NS))
        ver.text = version
        formt = etree.SubElement(node,
                                 qualify("format", NETCONF_MONITORING_NS))
        formt.text = reqformat
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_dispatch(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Dispatch(session, self.device_handler, raise_mode=RaiseMode.ALL)
        rpc = 'get-software-information'
        source = "candidate"
        root_filter = new_ele('filter')
        config_filter = sub_ele(root_filter, 'configuration')
        system_filter = sub_ele(config_filter, 'system')
        sub_ele(system_filter, 'services')
        a = copy.deepcopy(root_filter)
        obj.request(rpc, source=source, filter=a)
        node = new_ele(rpc)
        node.append(util.datastore_or_url("source", source))
        node.append(util.build_filter(root_filter))
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_dispatch_2(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Dispatch(session, self.device_handler, raise_mode=RaiseMode.ALL)
        node = new_ele('get-software-information')
        source = "candidate"
        root_filter = new_ele('filter')
        config_filter = sub_ele(root_filter, 'configuration')
        system_filter = sub_ele(config_filter, 'system')
        sub_ele(system_filter, 'services')
        a = copy.deepcopy(root_filter)
        obj.request(node, source=source, filter=a)
        node.append(util.datastore_or_url("source", source))
        node.append(util.build_filter(root_filter))
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_with_multi_subtree_filters(self, mock_request):
        result = '''
                <?xml version="1.0" encoding="UTF-8"?>
                <data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
                      xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <cont1 xmlns="urn:mod1">
                        <le1>test_mod1_001</le1>
                        <le2>this is a test-one example</le2>
                    </cont1>
                    <cont2 xmlns="urn:mod2">
                        <le1>test_mod2_002</le1>
                        <le2>this is a test-two example</le2>
                        <lst>
                            <le3>a list of mod2</le3>
                        </lst>
                    </cont2>
                </data>'''
        mock_request.return_value = result
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = Get(session, self.device_handler, raise_mode=RaiseMode.ALL)

        multi_subtree_filters = [
            '<cont1 xmlns="urn:mod1"> \
                <le1/> \
                <le2/> \
             </cont1>',
             '<cont2 xmlns="urn:mod2"/>'
        ]

        ret = obj.request(copy.deepcopy(multi_subtree_filters))
        node = new_ele("get")
        node.append(util.build_filter(multi_subtree_filters))
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)
        self.assertEqual(ret, result)

