from lxml import etree

from ncclient.xml_ import *
from ncclient.operations.rpc import RPC

class SaveConfig(RPC):
    def request(self, cmds):
        node = etree.Element(qualify('save-config', "http://cisco.com/yang/cisco-ia"))
        return self._request(node)
