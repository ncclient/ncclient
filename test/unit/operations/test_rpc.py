from ncclient.operations.rpc import *
import unittest
from mock import patch
from ncclient import manager
import ncclient.manager
import ncclient.transport
from ncclient.xml_ import *
from ncclient.operations import RaiseMode
from ncclient.capabilities import Capabilities
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


class TestRPC(unittest.TestCase):

    def test_rpc_reply(self):
        obj = RPCReply(xml4)
        obj.parse()
        self.assertTrue(obj.ok)
        self.assertFalse(obj.error)
        self.assertEqual(xml4, obj.xml)
        self.assertTrue(obj._parsed)

    @patch('ncclient.transport.Session.send')
    @patch(patch_str)
    def test_rpc_send(self, mock_thread, mock_send):
        device_handler = manager.make_device_handler({'name': 'junos'})
        capabilities = Capabilities(device_handler.get_capabilities())
        session = ncclient.transport.Session(capabilities)
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
    def test_rpc_async(self, mock_thread, mock_send):
        device_handler = manager.make_device_handler({'name': 'junos'})
        capabilities = Capabilities(device_handler.get_capabilities())
        session = ncclient.transport.Session(capabilities)
        obj = RPC(
            session,
            device_handler,
            raise_mode=RaiseMode.ALL,
            timeout=0,
            async=True)
        reply = RPCReply(xml1)
        obj._reply = reply
        node = new_ele("commit")
        result = obj._request(node)
        self.assertEqual(result, obj)

    @patch('ncclient.transport.Session.send')
    @patch(patch_str)
    def test_rpc_timeout_error(self, mock_thread, mock_send):
        device_handler = manager.make_device_handler({'name': 'junos'})
        capabilities = Capabilities(device_handler.get_capabilities())
        session = ncclient.transport.Session(capabilities)
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
        device_handler = manager.make_device_handler({'name': 'junos'})
        capabilities = Capabilities(device_handler.get_capabilities())
        session = ncclient.transport.Session(capabilities)
        obj = RPC(session, device_handler, raise_mode=RaiseMode.ALL, timeout=0)
        reply = RPCReply(xml1)
        obj._reply = reply
        node = new_ele("commit")
        sub_ele(node, "confirmed")

        err = RPCError(to_ele(xml2))
        obj.deliver_error(err)
        self.assertRaises(RPCError, obj._request, node)

    @patch('ncclient.transport.Session.send')
    @patch(patch_str)
    def test_rpc_capability_error(self, mock_thread, mock_send):
        device_handler = manager.make_device_handler({'name': 'junos'})
        capabilities = Capabilities(device_handler.get_capabilities())
        session = ncclient.transport.Session(capabilities)
        session._server_capabilities = [':running']
        obj = RPC(session, device_handler, raise_mode=RaiseMode.ALL, timeout=0)
        obj._assert(':running')
        self.assertRaises(MissingCapabilityError,
            obj._assert, ':candidate')
