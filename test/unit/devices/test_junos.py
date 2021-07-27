import unittest
from ncclient.devices.junos import *
import ncclient.transport
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
import paramiko
import sys

xml = '''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <xsl:output method="xml" indent="no"/>

        <xsl:template match="/|comment()|processing-instruction()">
            <xsl:copy>
                <xsl:apply-templates/>
            </xsl:copy>
        </xsl:template>

        <xsl:template match="*">
            <xsl:element name="{local-name()}">
                <xsl:apply-templates select="@*|node()"/>
            </xsl:element>
        </xsl:template>

        <xsl:template match="@*">
            <xsl:attribute name="{local-name()}">
                <xsl:value-of select="."/>
            </xsl:attribute>
        </xsl:template>
        </xsl:stylesheet>
        '''
xml2 = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/12.1X46/junos">
<routing-engine>
<name>reX</name>
<commit-success/>
<ok/>
</rpc-reply>"""

xml3 = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/12.1X46/junos">
<routing-engine>
<name>reX</name>
<commit-success/>
<routing-engine/>
<ok/>
</rpc-reply>"""

xml4 = """<rpc-reply>
<operation>commit</operation>
<name>reX</name>
<commit-success/>
<ok/>
</rpc-reply>
<rpc-error>
<message>commit failure</message>
</rpc-error>
<hello>greeting!</hello>"""


class TestJunosDevice(unittest.TestCase):

    def setUp(self):
        self.obj = JunosDeviceHandler({'name': 'junos'})

    @patch('paramiko.Channel.exec_command')
    @patch('paramiko.Transport.__init__')
    @patch('paramiko.Transport.open_channel')
    def test_handle_connection_exceptions(
            self, mock_open, mock_init, mock_channel):
        session = ncclient.transport.SSHSession(self.obj)
        session._channel_id = 100
        mock_init.return_value = None
        session._transport = paramiko.Transport()
        channel = paramiko.Channel(100)
        mock_open.return_value = channel
        self.obj.handle_connection_exceptions(session)
        self.assertEqual(channel._name, "netconf-command-100")
        self.assertEqual(
            mock_channel.call_args_list[0][0][0],
            "xml-mode netconf need-trailer")

    def test_additional_operations(self):
        dict = {}
        dict["rpc"] = ExecuteRpc
        dict["get_configuration"] = GetConfiguration
        dict["load_configuration"] = LoadConfiguration
        dict["compare_configuration"] = CompareConfiguration
        dict["command"] = Command
        dict["reboot"] = Reboot
        dict["halt"] = Halt
        dict["commit"] = Commit
        dict["rollback"] = Rollback
        self.assertEqual(dict, self.obj.add_additional_operations())

    def test_transform_reply(self):
        if sys.version >= '3':
            reply = xml.encode('utf-8')
        else:
            reply = xml
        self.assertEqual(self.obj.transform_reply(), reply)

    def test_perform_quality_check(self):
        self.assertFalse(self.obj.perform_qualify_check())

    def test_handle_raw_dispatch(self):
        self.assertFalse(self.obj.handle_raw_dispatch(xml))

        expected = re.sub(r'<ok/>', '</routing-engine>\n<ok/>', xml3)
        self.assertEqual(expected, self.obj.handle_raw_dispatch(xml3))

        expected = 'undefined: not an error message in the reply. Enable debug'
        self.assertEqual(expected, str(self.obj.handle_raw_dispatch(xml4)))
