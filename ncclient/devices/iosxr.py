"""
Handler for Cisco IOS-XR device specific information.

Note that for proper import, the classname has to be:

    "<Devicename>DeviceHandler"

...where <Devicename> is something like "Default", "Nexus", etc.

All device-specific handlers derive from the DefaultDeviceHandler, which implements the
generic information needed for interaction with a Netconf server.

"""

from ncclient.xml_ import BASE_NS_1_0
from ncclient.devices.default import DefaultDeviceHandler
from ncclient.operations.third_party.iosxr.rpc import ExecuteRpc, Get, GetConfiguration


def iosxr_unknown_host_cb(host, fingerprint):
    # This will ignore the unknown host check when connecting to IOS-XR devices
    return True


class IosxrDeviceHandler(DefaultDeviceHandler):

    """
    Cisco IOS-XR handler for device specific information.
    """

    _EXEMPT_ERRORS = [
        '*There is no message to reply.*'  # becasue the device replies with the following error
        # when sending hello message:
        # ERROR: 0xa367aa00 'XML Service Library' detected the 'fatal' condition 'There is no message to reply.'
        # simply clever.
    ]

    def __init__(self, device_params):
        super(IosxrDeviceHandler, self).__init__(device_params)

    def add_additional_operations(self):

        ops = {}

        ops['rpc'] = ExecuteRpc  # for arbitrary XML RPC reqs
        # get-config type RPC requsts might or might not have the <filter> tag
        ops['get'] = Get
        ops['get_config'] = GetConfiguration

        # others seem to respect the standard

        return ops

    def add_additional_ssh_connect_params(self, kwargs):

        kwargs['allow_agent'] = False
        kwargs['look_for_keys'] = False
        kwargs['hostkey_verify'] = False
        kwargs['unknown_host_cb'] = iosxr_unknown_host_cb

    def perform_qualify_check(self):
        return False

    def get_xml_base_namespace_dict(self):

        # default namespace
        return {None: BASE_NS_1_0}

    def get_xml_extra_prefix_kwargs(self):

        return {
            "nsmap": {
                None: BASE_NS_1_0
            }
        }

    def transform_reply(self):

        # filter rpc-reply, strip namespaces
        reply = '''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
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

        import sys
        if sys.version < '3':
            return reply
        else:
            return reply.encode('UTF-8')
