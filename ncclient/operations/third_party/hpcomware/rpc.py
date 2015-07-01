from lxml import etree

from ncclient.xml_ import *
from ncclient.operations.rpc import RPC

class CLICommand(RPC):
    def request(self, cmds):
        node = etree.Element(qualify('CLI', BASE_NS_1_0))
        print node, '^^^'

        for cmd in cmds:
            etree.SubElement(node, qualify('Execution', BASE_NS_1_0)).text = cmd

        print node, '***'

        return self._request(node)
