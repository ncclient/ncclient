import os

import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
import paramiko

from ncclient import manager
from ncclient.transport.ssh import SSHSession
from ncclient.operations.third_party.juniper.rpc import *
from ncclient.operations import RaiseMode
from ncclient.transport.parser import DefaultXMLParser

try:
    import selectors
except ImportError:
    import selectors2 as selectors


class TestSession(unittest.TestCase):

    @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
    @patch('ncclient.transport.SSHSession.connected')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('ncclient.transport.SSHSession')
    @patch('selectors.DefaultSelector.select')
    @patch('ncclient.operations.rpc.uuid4')
    def test_filter_xml_sax_on(self, mock_uuid4, mock_select, mock_session, mock_recv,
                              mock_close, mock_send, mock_send_ready, mock_connected):
        mock_send.return_value = True
        mock_send_ready.return_value = -1
        mock_uuid4.return_value = type('dummy', (), {'urn': "urn:uuid:e0a7abe3-fffa-11e5-b78e-b8e85604f858"})
        device_handler = manager.make_device_handler({'name': 'junos', 'use_filter': True})
        rpc = '<get-software-information/>'
        mock_recv.side_effect = self._read_file('get-software-information.xml')
        session = SSHSession(device_handler)
        session._connected = True
        session._channel = paramiko.Channel("c100")
        session.parser = session._device_handler.get_xml_parser(session)
        obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
        obj._filter_xml = '<multi-routing-engine-results><multi-routing-engine-item><re-name/></multi-routing-engine-item></multi-routing-engine-results>'
        session.run()
        resp = obj.request(rpc)._NCElement__doc[0]
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/re-name')), 2)
        # as filter_xml is not having software-information, response wont contain it
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/software-information')), 0)

    @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
    @patch('ncclient.transport.SSHSession.connected')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('ncclient.transport.SSHSession')
    @patch('selectors.DefaultSelector.select')
    @patch('ncclient.operations.rpc.uuid4')
    def test_filter_xml_sax_on_junos_rfc_compliant(self, mock_uuid4, mock_select, mock_session, mock_recv,
                              mock_close, mock_send, mock_send_ready, mock_connected):
        mock_send.return_value = True
        mock_send_ready.return_value = -1
        mock_uuid4.return_value = type('dummy', (), {'urn': "urn:uuid:e0a7abe3-fffa-11e5-b78e-b8e85604f858"})
        device_handler = manager.make_device_handler({'name': 'junos', 'use_filter': True})
        rpc = '<get-software-information/>'
        mock_recv.side_effect = self._read_file('get-software-information.xml')
        session = SSHSession(device_handler)
        session._connected = True
        session._channel = paramiko.Channel("c100")
        session.parser = session._device_handler.get_xml_parser(session)
        obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
        obj._filter_xml = '<multi-routing-engine-results><multi-routing-engine-item><re-name/></multi-routing-engine-item></multi-routing-engine-results>'
        session.run()
        resp = obj.request(rpc)._NCElement__doc[0]
        from lxml import etree
        print(resp)
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/re-name')), 2)
        # as filter_xml is not having software-information, response wont contain it
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/software-information')), 0)
        
    @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
    @patch('ncclient.transport.SSHSession.connected')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('ncclient.transport.SSHSession')
    @patch('selectors.DefaultSelector.select')
    @patch('ncclient.operations.rpc.uuid4')
    def test_filter_xml_delimiter_rpc_reply(self, mock_uuid4, mock_select,
                                            mock_session, mock_recv, mock_close,
                                            mock_send, mock_send_ready,
                                            mock_connected):
        mock_send.return_value = True
        mock_send_ready.return_value = -1
        mock_uuid4.return_value = type('dummy', (), {'urn': "urn:uuid:e0a7abe3-fffa-11e5-b78e-b8e85604f858"})
        device_handler = manager.make_device_handler({'name': 'junos', 'use_filter': True})
        rpc = '<get-software-information/>'
        mock_recv.side_effect = self._read_file('get-software-information.xml')[:-1] + [b"</rpc-reply>]]>", b"]]>"]
        session = SSHSession(device_handler)
        session._connected = True
        session._channel = paramiko.Channel("c100")
        session.parser = session._device_handler.get_xml_parser(session)
        obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
        obj._filter_xml = '<multi-routing-engine-results><multi-routing-engine-item><re-name/></multi-routing-engine-item></multi-routing-engine-results>'
        session.run()
        resp = obj.request(rpc)._NCElement__doc[0]
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/re-name')), 2)
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/software-information')), 0)

    @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
    @patch('ncclient.transport.SSHSession.connected')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('ncclient.transport.SSHSession')
    @patch('selectors.DefaultSelector.select')
    @patch('ncclient.operations.rpc.uuid4')
    def test_filter_xml_delimiter_multiple_rpc_reply(self, mock_uuid4, mock_select,
                                            mock_session, mock_recv, mock_close,
                                            mock_send, mock_send_ready,
                                            mock_connected):
        mock_send.return_value = True
        mock_send_ready.return_value = -1
        mock_uuid4.return_value = type('dummy', (), {'urn': "urn:uuid:e0a7abe3-fffa-11e5-b78e-b8e85604f858"})
        device_handler = manager.make_device_handler({'name': 'junos', 'use_filter': True})
        rpc = '<get-software-information/>'
        mock_recv.side_effect = self._read_file('get-software-information.xml')[:-1] + [b"</rpc-reply>]]>",
                                                                                        b"]]><rpc-reply>"] + \
                                self._read_file('get-software-information.xml')[1:]
        session = SSHSession(device_handler)
        session._connected = True
        session._channel = paramiko.Channel("c100")
        session.parser = session._device_handler.get_xml_parser(session)
        obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
        obj._filter_xml = '<multi-routing-engine-results><multi-routing-engine-item><re-name/></multi-routing-engine-item></multi-routing-engine-results>'
        session.run()
        resp = obj.request(rpc)._NCElement__doc[0]
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/re-name')), 2)
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/software-information')), 0)

        @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
        @patch('ncclient.transport.SSHSession.connected')
        @patch('paramiko.channel.Channel.send_ready')
        @patch('paramiko.channel.Channel.send')
        @patch('ncclient.transport.ssh.SSHSession.close')
        @patch('paramiko.channel.Channel.recv')
        @patch('ncclient.transport.SSHSession')
        @patch('selectors.DefaultSelector.select')
        @patch('ncclient.operations.rpc.uuid4')
        def test_filter_xml_delimiter_multiple_rpc_in_parallel(self, mock_uuid4, mock_select,
                                                               mock_session, mock_recv, mock_close,
                                                               mock_send, mock_send_ready,
                                                               mock_connected):
            mock_send.return_value = True
            mock_send_ready.return_value = -1
            mock_uuid4.side_effect = [type('xyz', (), {'urn': "urn:uuid:ddef40cb-5745-481d-974d-7188f9f2bb33"}),
                                      type('pqr', (), {'urn': "urn:uuid:549ef9d1-024a-4fd0-88bf-047d25f0870d"})]
            device_handler = manager.make_device_handler({'name': 'junos', 'use_filter': True})
            rpc = '<get-software-information/>'
            mock_recv.side_effect = [b"""
            <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:junos="http://xml.juniper.net/junos/19.2I0/junos" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:ddef40cb-5745-481d-974d-7188f9f2bb33">
    <ospf-neighbor-information xmlns="http://xml.juniper.net/junos/19.2I0/junos-routing">
    <ospf-neighbor>
    <neighbor-address>13.1.1.2</neighbor-address>
    <interface-name>ge-0/0/0.1</interface-name>
    <ospf-neighbor-state>Exchange</ospf-neighbor-state>
    <neighbor-id>2.2.2.2</neighbor-id>
    <neighbor-priority>128</neighbor-priority>
    <activity-timer>36</activity-timer>
    <ospf-area>0.0.0.0</ospf-area>
    <options>0x52</options>
    <dr-address>13.1.1.1</dr-address>
    <bdr-address>13.1.1.2</bdr-address>
    <neighbor-up-time junos:seconds="17812">
    04:56:52
    </neighbor-up-time>
    <neighbor-adjacency-time junos:seconds="17812">
    04:56:52
    </neighbor-adjacency-time>
    <master-slave>slave</master-slave>
    <sequence-number>0x204b6fd</sequence-number>
    <dbd-retransmit-time>3</dbd-retransmit-time>
    <lsreq-retransmit-time>0</lsreq-retransmit-time>
    <lsa-list>
      Link state retransmission list:
        Type      LSA ID           Adv rtr          Seq
       Router    1.1.1.1          1.1.1.1          0x80000019
       OpaqArea  1.0.0.1          1.1.1.1          0x80000011
       Router    3.3.3.3          3.3.3.3          0x80000004
       Network   23.1.1.2         3.3.3.3          0x80000001
       OpaqArea  1.0.0.1          2.2.2.2          0x80000002
       OpaqArea  1.0.0.1          3.3.3.3          0x80000002
       OpaqArea  1.0.0.3          1.1.1.1          0x80000002
       OpaqArea  1.0.0.3          3.3.3.3          0x80000001
       OpaqArea  1.0.0.4          2.2.2.2          0x80000001
    </lsa-list>
    <ospf-neighbor-topology>
    <ospf-topology-name>default</ospf-topology-name>
    <ospf-topology-id>0</ospf-topology-id>
    <ospf-neighbor-topology-state>Forward Only</ospf-neighbor-topology-state>
    </ospf-neighbor-topology>
    </ospf-neighbor>
    </ospf-neighbor-information>
    </rpc-reply>]]>]]><rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:junos="http://xml.juniper.net/junos/19.2I0/junos" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:549ef9d1-024a-4fd0-88bf-047d25f0870d">
    <pfe-statistics>
    <pfe-traffic-statistics>
    <pfe-input-packets>22450</pfe-input-packets>
    <input-pps>0</input-pps>
    <pfe-output-packets>31992</pfe-output-packets>
    <output-pps>0</output-pps>
    <pfe-fabric-input>0</pfe-fabric-input>
    <pfe-fabric-input-pps>0</pfe-fabric-input-pps>
    <pfe-fabric-output>0</pfe-fabric-output>
    <pfe-fabric-output-pps>0</pfe-fabric-output-pps>
    </pfe-traffic-statistics></pfe-statistics></rpc-reply>]]>]]>"""]
            session = SSHSession(device_handler)
            session._connected = True
            session._channel = paramiko.Channel("c100")
            session.parser = session._device_handler.get_xml_parser(session)
            obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
            obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
            obj._filter_xml = '<multi-routing-engine-results><multi-routing-engine-item><re-name/></multi-routing-engine-item></multi-routing-engine-results>'
            session.run()
            resp = obj.request(rpc)._NCElement__doc[0]
            self.assertEqual(len(resp.xpath('pfe-traffic-statistics')), 1)

    @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
    @patch('ncclient.transport.SSHSession.connected')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('ncclient.transport.SSHSession')
    @patch('selectors.DefaultSelector.select')
    @patch('ncclient.operations.rpc.uuid4')
    def test_filter_xml_delimiter_splited_rpc_reply(self, mock_uuid4, mock_select,
                                            mock_session, mock_recv, mock_close,
                                            mock_send, mock_send_ready,
                                            mock_connected):
        mock_send.return_value = True
        mock_send_ready.return_value = -1
        mock_uuid4.return_value = type('dummy', (), {'urn': "urn:uuid:e0a7abe3-fffa-11e5-b78e-b8e85604f858"})
        device_handler = manager.make_device_handler({'name': 'junos', 'use_filter': True})
        rpc = '<get-software-information/>'
        mock_recv.side_effect = self._read_file('get-software-information.xml')[:-1] + [b"</rpc", b"-reply>]]>",
                                                                                        b"]]><rpc-reply>"] + \
                                self._read_file('get-software-information.xml')[1:]
        session = SSHSession(device_handler)
        session._connected = True
        session._channel = paramiko.Channel("c100")
        session.parser = session._device_handler.get_xml_parser(session)
        obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
        obj._filter_xml = '<multi-routing-engine-results><multi-routing-engine-item><re-name/></multi-routing-engine-item></multi-routing-engine-results>'
        session.run()
        resp = obj.request(rpc)._NCElement__doc[0]
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/re-name')), 2)
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/software-information')), 0)

    @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
    @patch('ncclient.transport.SSHSession.connected')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('ncclient.transport.SSHSession')
    @patch('selectors.DefaultSelector.select')
    @patch('ncclient.operations.rpc.uuid4')
    def test_use_filter_xml_without_sax_input(self, mock_uuid4, mock_select,
                                              mock_session, mock_recv,
                                              mock_close, mock_send,
                                              mock_send_ready,
                                              mock_connected):
        mock_send.return_value = True
        mock_send_ready.return_value = -1
        mock_uuid4.return_value = type('dummy', (), {'urn': "urn:uuid:e0a7abe3-fffa-11e5-b78e-b8e85604f858"})
        device_handler = manager.make_device_handler({'name': 'junos', 'use_filter': True})
        rpc = '<get-software-information/>'
        mock_recv.side_effect = self._read_file('get-software-information.xml')
        session = SSHSession(device_handler)
        session._connected = True
        session._channel = paramiko.Channel("c100")
        session.parser = session._device_handler.get_xml_parser(session)
        obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
        obj._filter_xml = None
        session.run()
        resp = obj.request(rpc)._NCElement__doc[0]
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/re-name')), 2)
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/software-information')), 2)

    @unittest.skipIf(sys.version_info.major == 2, "test not supported < Python3")
    @patch('ncclient.transport.SSHSession.connected')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('ncclient.transport.SSHSession')
    @patch('selectors.DefaultSelector.select')
    @patch('ncclient.operations.rpc.uuid4')
    def test_use_filter_False(self, mock_uuid4, mock_select,
                                              mock_session, mock_recv,
                                              mock_close, mock_send,
                                              mock_send_ready,
                                              mock_connected):
        mock_send.return_value = True
        mock_send_ready.return_value = -1
        mock_uuid4.return_value = type('dummy', (), {'urn': "urn:uuid:e0a7abe3-fffa-11e5-b78e-b8e85604f858"})
        device_handler = manager.make_device_handler({'name': 'junos', 'use_filter': False})
        rpc = '<get-software-information/>'
        mock_recv.side_effect = self._read_file('get-software-information.xml')
        session = SSHSession(device_handler)
        session._connected = True
        session._channel = paramiko.Channel("c100")
        session.parser = session._device_handler.get_xml_parser(session)
        obj = ExecuteRpc(session, device_handler, raise_mode=RaiseMode.ALL)
        obj._filter_xml = '<multi-routing-engine-results><multi-routing-engine-item><re-name/></multi-routing-engine-item></multi-routing-engine-results>'
        session.run()
        resp = obj.request(rpc)._NCElement__doc[0]
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/re-name')), 2)
        # as filter_xml is not having software-information, response wont contain it
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/software-information')), 2)
        self.assertIsInstance(session.parser, DefaultXMLParser)

    def _read_file(self, fname):
        fpath = os.path.join(os.path.dirname(__file__),
                             'rpc-reply', fname)
        lines = []
        with open(fpath, "rb") as fp:
            lines = fp.readlines()
        return lines
