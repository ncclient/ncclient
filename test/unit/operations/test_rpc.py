from ncclient.operations.rpc import *
import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient import manager
import ncclient.manager
import ncclient.transport
from ncclient.xml_ import *
from ncclient.operations import RaiseMode
from ncclient.capabilities import Capabilities
from xml.sax.saxutils import escape
import sys

if sys.version >= '3':
    patch_str = 'ncclient.operations.rpc.Event.isSet'
else:
    patch_str = 'threading._Event.isSet'

xml1 = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/12.1X46/junos">
    <ok/>
</rpc-reply>"""

xml2 = """<rpc-reply message-id="urn:uuid:15ceca00-904e-11e4-94ad-5c514f91ab3f">
	<load-configuration-results>
		<rpc-error>
			<error-severity>error</error-severity>
			<error-info>
				<bad-element>system1</bad-element>
			</error-info>
			<error-message>syntax error</error-message>
		</rpc-error>
		<rpc-error>
			<error-severity>error</error-severity>
			<error-info>
				<bad-element>}</bad-element>
			</error-info>
            <error-message>error recovery ignores input until this point</error-message>
		</rpc-error>
	</load-configuration-results>
</rpc-reply>"""

xml3 = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/12.1X46/junos" attrib1 = "test">
    <software-information>
        <host-name>R1</host-name>
        <product-model>firefly-perimeter</product-model>
        <product-name>firefly-perimeter</product-name>
        <package-information>
            <name>junos</name>
            <comment>JUNOS Software Release [12.1X46-D10.2]</comment>
        </package-information>
    </software-information>
    <rpc-error>
    </rpc-error>
    <cli>
        <banner></banner>
    </cli>
</rpc-reply>"""

xml4 = """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:junos="http://xml.juniper.net/junos/14.2I0/junos" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:b19400d6-fa2a-11e4-8f7b-0800278ff596">
<data>
<configuration xmlns="http://xml.juniper.net/xnm/1.1/xnm" junos:changed-seconds="1431599824" junos:changed-localtime="2015-05-14 03:37:04 PDT">
    <system>
        <services>
            <ftp>
                <connection-limit>200</connection-limit>
                <rate-limit>214</rate-limit>
            </ftp>
            <ssh>
                <root-login>allow</root-login>
            </ssh>
            <telnet>
            </telnet>
            <netconf>
                <ssh>
                </ssh>
            </netconf>
        </services>
    </system>
</configuration>
</data>
</rpc-reply>"""

# Huge dummy text configuration to trigger "xml.etree.XMLSyntaxError: xmlSAX2Characters: huge text node"
# - The maximum size of a single text node is `#define XML_MAX_TEXT_LENGTH 10000000`
#   (https://gitlab.gnome.org/GNOME/libxml2/blob/master/include/libxml/parserInternals.h)
# - The text should contain at least one special character that should be escaped (e.g. '>')
huge_configuration_text = "-->\n" + "Huge configuration. " * 500000

xml5_huge = """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:junos="http://xml.juniper.net/junos/18.2R1/junos" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:b8b20a95-7822-4c59-97a3-44435d6fc6a7">
<configuration-text xmlns="http://xml.juniper.net/xnm/1.1/xnm">%s</configuration-text>
</rpc-reply>""" % escape(huge_configuration_text)

xml6 = """<rpc-error xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
			<error-type>application</error-type>
			<error-tag>invalid-value</error-tag>
			<error-severity>error</error-severity>
			<error-path>path/to/node</error-path>
			<error-info>
				<bad-element>system1</bad-element>
			</error-info>
			<error-app-tag>app-tag1</error-app-tag>
			<error-message>syntax error</error-message>
	  </rpc-error>
"""

xml7 = """<rpc-error xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
			<error-type>protocol</error-type>
			<error-tag>missing-element</error-tag>
			<error-severity>error</error-severity>
			<error-path>path/to/different/node</error-path>
			<error-info>
				<bad-element>system2</bad-element>
			</error-info>
			<error-app-tag>app-tag2</error-app-tag>
			<error-message>missing element error</error-message>
	  </rpc-error>
"""

class TestRPC(unittest.TestCase):

    def test_rpc_reply(self):
        obj = RPCReply(xml4)
        obj.parse()
        self.assertTrue(obj.ok)
        self.assertFalse(obj.error)
        self.assertEqual(xml4, obj.xml)
        self.assertTrue(obj._parsed)

    def test_rpc_reply_huge_text_node_exception(self):
        obj = RPCReply(xml5_huge)
        self.assertRaises(etree.XMLSyntaxError, obj.parse)

    def test_rpc_reply_huge_text_node_workaround(self):
        obj = RPCReply(xml5_huge, huge_tree=True)
        obj.parse()
        self.assertTrue(obj.ok)
        self.assertFalse(obj.error)
        self.assertEqual(xml5_huge, obj.xml)
        self.assertTrue(obj._parsed)

    @patch('ncclient.transport.Session.send')
    @patch(patch_str)
    def test_rpc_send(self, mock_thread, mock_send):
        device_handler, session = self._mock_device_handler_and_session()
        obj = RPC(session, device_handler, raise_mode=RaiseMode.ALL, timeout=0)
        reply = RPCReply(xml1)
        obj._reply = reply
        node = new_ele("commit")
        sub_ele(node, "confirmed")
        sub_ele(node, "confirm-timeout").text = "50"
        sub_ele(node, "log").text = "message"
        result = obj._request(node)
        ele = new_ele("rpc",
                      {"message-id": obj._id},
                      **device_handler.get_xml_extra_prefix_kwargs())
        ele.append(node)
        node = to_xml(ele)
        mock_send.assert_called_once_with(node)
        self.assertEqual(
            result.data_xml,
            (NCElement(
                reply,
                device_handler.transform_reply())).data_xml)
        self.assertEqual(obj.session, session)
        self.assertEqual(reply, obj.reply)

    @patch('ncclient.transport.Session.send')
    @patch(patch_str)
    def test_generic_rpc_send(self, mock_thread, mock_send):
        device_handler, session = self._mock_device_handler_and_session()
        obj = GenericRPC(session, device_handler, raise_mode=RaiseMode.ALL, timeout=0)
        reply = RPCReply(xml1)
        obj._reply = reply
        rpc_command = 'edit-config'
        filters = ('subtree', '<top xmlns="urn:mod1"/>')

        result = obj.request(rpc_command, source='running', target='candidate', filter=filters)
        ele = new_ele("rpc",
                      {"message-id": obj._id},
                      **device_handler.get_xml_extra_prefix_kwargs())
        child = new_ele(rpc_command)
        child.append(util.datastore_or_url('target', 'candidate'))
        child.append(util.datastore_or_url('source', 'running'))
        child.append(util.build_filter(filters))

        ele.append(child)
        node = to_xml(ele)
        mock_send.assert_called_once_with(node)
        self.assertEqual(
            result.data_xml,
            (NCElement(
                reply,
                device_handler.transform_reply())).data_xml)
        self.assertEqual(obj.session, session)
        self.assertEqual(reply, obj.reply)

    @patch('ncclient.transport.Session.send')
    @patch(patch_str)
    def test_rpc_async(self, mock_thread, mock_send):
        device_handler, session = self._mock_device_handler_and_session()
        obj = RPC(
            session,
            device_handler,
            raise_mode=RaiseMode.ALL,
            timeout=0,
            async_mode=True)
        reply = RPCReply(xml1)
        obj._reply = reply
        node = new_ele("commit")
        result = obj._request(node)
        self.assertEqual(result, obj)

    @patch('ncclient.transport.Session.send')
    @patch(patch_str)
    def test_rpc_timeout_error(self, mock_thread, mock_send):
        device_handler, session = self._mock_device_handler_and_session()
        obj = RPC(session, device_handler, raise_mode=RaiseMode.ALL, timeout=0)
        reply = RPCReply(xml1)
        obj.deliver_reply(reply)
        node = new_ele("commit")
        sub_ele(node, "confirmed")
        mock_thread.return_value = False
        self.assertRaises(TimeoutExpiredError, obj._request, node)

    @patch('ncclient.transport.Session.send')
    @patch(patch_str)
    def test_rpc_rpcerror(self, mock_thread, mock_send):
        device_handler, session = self._mock_device_handler_and_session()
        obj = RPC(session, device_handler, raise_mode=RaiseMode.ALL, timeout=0)
        reply = RPCReply(xml1)
        obj._reply = reply
        node = new_ele("commit")
        sub_ele(node, "confirmed")

        err = RPCError(to_ele(xml2))
        obj.deliver_error(err)
        self.assertRaises(RPCError, obj._request, node)

    def test_rpc_rpcerror_tag_to_attr(self):
        '''All elements in <rpc-error> extracted.'''
        err = RPCError(to_ele(xml6))

        self.assertEqual(None, err.errlist)

        self.assertEqual("application", err.type)
        self.assertEqual("invalid-value", err.tag)
        self.assertEqual("error", err.severity)
        self.assertEqual("path/to/node", err.path)
        self.assertEqual("app-tag1", err.app_tag)
        self.assertEqual("syntax error", err.message)
        self.assertIn("<bad-element>system1</bad-element>", err.info)

    def test_rpc_rpcerror_multiple_errors(self):
        '''Multiple errors in <rpc-reply> extracted correctly'''
        errlist = [RPCError(to_ele(xml6)), RPCError(to_ele(xml7))]

        multiple_xml = (
        '<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">' +
        xml6 + xml7 +
        "</rpc-reply>")

        multiple_err = RPCError(to_ele(multiple_xml), errs=errlist)
        errs = multiple_err.errlist

        self.assertEqual(2, len(errs))

        self.assertEqual("application", errs[0].type)
        self.assertEqual("invalid-value", errs[0].tag)
        self.assertEqual("error", errs[0].severity)
        self.assertEqual("path/to/node", errs[0].path)
        self.assertEqual("app-tag1", errs[0].app_tag)
        self.assertEqual("syntax error", errs[0].message)
        self.assertIn("<bad-element>system1</bad-element>", errs[0].info)

        self.assertEqual("protocol", errs[1].type)
        self.assertEqual("missing-element", errs[1].tag)
        self.assertEqual("error", errs[1].severity)
        self.assertEqual("path/to/different/node", errs[1].path)
        self.assertEqual("app-tag2", errs[1].app_tag)
        self.assertEqual("missing element error", errs[1].message)
        self.assertIn("<bad-element>system2</bad-element>", errs[1].info)

    @patch('ncclient.transport.Session.send')
    @patch(patch_str)
    def test_rpc_capability_error(self, mock_thread, mock_send):
        device_handler, session = self._mock_device_handler_and_session()
        session._server_capabilities = [':running']
        obj = RPC(session, device_handler, raise_mode=RaiseMode.ALL, timeout=0)
        obj._assert(':running')
        self.assertRaises(MissingCapabilityError,
            obj._assert, ':candidate')

    @patch('ncclient.transport.Session.send')
    def test_rpc_huge_text_node_exception(self, mock_send):
        device_handler, session = self._mock_device_handler_and_session()
        obj = RPC(session, device_handler, raise_mode=RaiseMode.ALL, timeout=0)

        obj.deliver_reply(xml5_huge)
        node = new_ele("get-configuration", {'format': 'text'})
        self.assertRaises(etree.XMLSyntaxError, obj._request, node)

    @patch('ncclient.transport.Session.send')
    def test_rpc_huge_text_node_workaround(self, mock_send):
        device_handler, session = self._mock_device_handler_and_session()
        obj = RPC(session, device_handler, raise_mode=RaiseMode.ALL, timeout=0, huge_tree=True)
        self.assertTrue(obj.huge_tree)

        obj.deliver_reply(xml5_huge)
        node = new_ele("get-configuration", {'format': 'text'})
        result = obj._request(node)

        self.assertEqual(result.find('configuration-text').text, huge_configuration_text)
        obj.huge_tree = False
        self.assertFalse(obj.huge_tree)

    def _mock_device_handler_and_session(self):
        device_handler = manager.make_device_handler({'name': 'junos'})
        capabilities = Capabilities(device_handler.get_capabilities())
        session = ncclient.transport.Session(capabilities)
        return device_handler, session
