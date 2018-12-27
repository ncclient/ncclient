import os

import unittest
from mock import patch
import paramiko

from ncclient import manager
from ncclient.transport.ssh import SSHSession
from ncclient.operations.third_party.juniper.rpc import *
from ncclient.operations import RaiseMode


class TestSession(unittest.TestCase):
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

    @patch('ncclient.transport.SSHSession.connected')
    @patch('paramiko.channel.Channel.send_ready')
    @patch('paramiko.channel.Channel.send')
    @patch('ncclient.transport.ssh.SSHSession.close')
    @patch('paramiko.channel.Channel.recv')
    @patch('ncclient.transport.SSHSession')
    @patch('selectors.DefaultSelector.select')
    @patch('ncclient.operations.rpc.uuid4')
    def test_filter_xml_sax_off(self, mock_uuid4, mock_select, mock_session, mock_recv,
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
        obj._filter_xml = None
        session.run()
        resp = obj.request(rpc)._NCElement__doc[0]
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/re-name')), 2)
        self.assertEqual(len(resp.xpath('multi-routing-engine-item/software-information')), 2)

    def _read_file(self, fname):
        fpath = os.path.join(os.path.dirname(__file__),
                             'rpc-reply', fname)
        lines = []
        with open(fpath, "rb") as fp:
            lines = fp.readlines()
        return lines
