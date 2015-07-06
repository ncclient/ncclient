from lxml import etree
from ncclient.xml_ import *
from ncclient.operations.rpc import RPC


class CLICommand(RPC):
    def request(self, cmds, cmd_type=None):
        """
        Single Execution/Configuration element is permitted.
        Execution is used for display commands while
        Configuration is used for config (system-view) commands
        cmds can be a list or single command
        """
        NETCONFBASE_C = "{urn:ietf:params:xml:ns:netconf:base:1.0}"

        if isinstance(cmds, list):
            cmd = '\n'.join(cmds)
        elif isinstance(cmds, str) or isinstance(cmds, unicode):
            cmd = cmds

        node = etree.Element(qualify('CLI', BASE_NS_1_0))

        if cmd_type == 'display':
            etree.SubElement(node, qualify('Execution',
                                           BASE_NS_1_0)).text = cmd
            response = self._request(node)
            xml_resp = etree.fromstring(response.xml)
            text = xml_resp.find('.//{0}Execution'.format(NETCONFBASE_C)).text

        elif cmd_type == 'config':
            etree.SubElement(node, qualify('Configuration',
                                           BASE_NS_1_0)).text = cmd

            response = self._request(node)
            xml_resp = etree.fromstring(response.xml)
            text = xml_resp.find('.//{0}Configuration'.format(NETCONFBASE_C)).text

        if text:
            text = text.replace('\n\n\n', '\n')
            text = text.replace('\n\n', '\n')

        return text
