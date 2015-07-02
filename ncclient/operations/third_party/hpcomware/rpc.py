from lxml import etree
from ncclient.xml_ import *
from ncclient.operations.rpc import RPC


class CLICommand(RPC):
    def request(self, cmds):
        """
        Single Execution element is permitted.
        cmds can be a list or single command
        """

        if isinstance(cmds, list):
            cmd = '\n'.join(cmds)
        elif isinstance(cmds, str) or isinstance(cmds, unicode):
            cmd = cmds

        node = etree.Element(qualify('CLI', BASE_NS_1_0))

        etree.SubElement(node, qualify('Execution',
                                       BASE_NS_1_0)).text = cmd

        return self._request(node)
