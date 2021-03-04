import copy
import unittest

import ncclient.manager
import ncclient.transport

from lxml import etree
from mock import patch
from ncclient import manager
from ncclient._types import Datastore
from ncclient._types import FilterType
from ncclient._types import WithDefaults
from ncclient.capabilities import Capabilities
from ncclient.namespaces import IETF
from ncclient.operations import RaiseMode
from ncclient.operations.errors import MissingCapabilityError
from ncclient.operations.retrieve import *
from ncclient.xml_ import *
from xml.etree import ElementTree

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
        self.assertRaisesRegexp(
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
    def test_get_data(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        obj.request(datastore=datastore)
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_config_filter(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        obj.request(datastore=datastore, config_filter=True)
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        sub_ele(node, 'config-filter').text = 'true'
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_subtree_filter(self, mock_request):
        filter_data = '''
        <netconf-state xmlns="%s">
          <schemas/>
        </netconf-state>''' % (IETF.nsmap['ncm'])
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        filter_type = FilterType.SUBTREE
        obj.request(datastore=datastore, filter=(filter_type, filter_data))
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        subtree_filter = sub_ele(node, 'subtree-filter')
        subtree_filter.append(to_ele(filter_data))
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_xpath_filter(self, mock_request):
        filter_data = '/interfaces/interface/state'
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        filter_type = FilterType.XPATH
        obj.request(datastore=datastore, filter=(filter_type, filter_data))
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        xpath_filter = sub_ele(node, 'xpath-filter')
        xpath_filter.text = filter_data
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_xpath_filter_with_ns(self, mock_request):
        filter_data = '/ncm:netconf-state/ncm:schemas'
        nsmap = {'ncm': IETF.nsmap['ncm']}
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        filter_type = FilterType.XPATH
        obj.request(datastore=datastore, filter=(filter_type, (nsmap, filter_data)))
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        xpath_filter = sub_ele_nsmap(node, 'xpath-filter', nsmap)
        xpath_filter.text = filter_data
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_origin_filters(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        origin_filters = [Origin.INTENDED]
        obj.request(datastore=datastore, origin_filters=origin_filters)
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        for origin_filter in origin_filters:
            of = sub_ele(node, 'origin-filter')
            of.text = 'or:' + origin_filter.name.lower()
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_multi_origin_filters(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        origin_filters = [Origin.INTENDED, Origin.SYSTEM]
        obj.request(datastore=datastore, origin_filters=origin_filters)
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        for origin_filter in origin_filters:
            of = sub_ele(node, 'origin-filter')
            of.text = 'or:' + origin_filter.name.lower()
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_negated_origin_filters(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        origin_filters = [Origin.INTENDED]
        obj.request(datastore=datastore,
                negated_origin_filters=origin_filters)
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        for origin_filter in origin_filters:
            of = sub_ele(node, 'negated-origin-filter')
            of.text = 'or:' + origin_filter.name.lower()
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_multi_negated_origin_filters(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        origin_filters = [Origin.INTENDED, Origin.SYSTEM]
        obj.request(datastore=datastore,
                negated_origin_filters=origin_filters)
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        for origin_filter in origin_filters:
            of = sub_ele(node, 'negated-origin-filter')
            of.text = 'or:' + origin_filter.name.lower()
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_max_depth(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        obj.request(datastore=datastore, max_depth=5)
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        sub_ele(node, 'max-depth').text = '5'
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_with_origin(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        obj.request(datastore=datastore, with_origin=True)
        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})
        ds_node = sub_ele(node, 'datastore',
                nsmap={'ds': IETF.nsmap['ds']})
        ds_node.text = 'ds:' + datastore.name.lower()
        sub_ele(node, 'with-origin')
        xml = ElementTree.tostring(node)
        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        self.assertEqual(call, xml)

    @patch('ncclient.operations.retrieve.RPC._request')
    def test_get_data_with_defaults(self, mock_request):
        session = ncclient.transport.SSHSession(self.device_handler)
        session._server_capabilities = Capabilities([
            "urn:ietf:params:netconf:capability:with-defaults:1.0"
            "?basic-mode=explicit"
            "&also-supported=report-all,trim"
        ])
        obj = GetData(session, self.device_handler, raise_mode=RaiseMode.ALL)
        datastore = Datastore.CANDIDATE
        with_defaults = WithDefaults.REPORT_ALL
        obj.request(datastore=datastore, with_defaults=with_defaults)

        expected_xml = etree.fromstring(
            '<ns0:get-data xmlns:ns0="{}" xmlns:ns1="{}" xmlns="{}">'
            '<ns0:datastore>ds:candidate</ns0:datastore>'
            '<ns1:with-defaults>report-all</ns1:with-defaults>'
            '</ns0:get-data>'.format(
                IETF.nsmap['nc'], IETF.nsmap['ncwd'], IETF.nsmap['ncds']
            )
        )

        call = mock_request.call_args_list[0][0][0]
        call = ElementTree.tostring(call)
        xml = etree.tostring(expected_xml)
        self.assertEqual(call, xml)

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

