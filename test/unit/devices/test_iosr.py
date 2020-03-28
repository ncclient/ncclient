import unittest
from ncclient.devices.iosxr import *
import ncclient.transport
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


class TestIOSXRDevice(unittest.TestCase):

    def setUp(self):
        self.obj = IosxrDeviceHandler({'name': 'iosxr'})

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
        self.assertEqual(dict, self.obj.add_additional_operations())
