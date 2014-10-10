from lxml import etree

from ncclient.xml_ import *
from ncclient.operations.rpc import RPC

class ExecCommand(RPC):
    def request(self, cmd):
        parent_node = etree.Element(qualify('exec-command', NXOS_1_0))
        child_node = etree.SubElement(parent_node, qualify('cmd', NXOS_1_0))
        child_node.text = cmd
        return self._request(parent_node)
