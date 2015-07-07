from lxml import etree
from ncclient.xml_ import *
from ncclient.operations.rpc import RPC


class DisplayCommand(RPC):
    def request(self, cmds, push=True):
        """
        Single Execution element is permitted.
        cmds can be a list or single command
        when push is set to True, otherwise, the element object
        is returned
        """

        if isinstance(cmds, list):
            cmd = '\n'.join(cmds)
        elif isinstance(cmds, str) or isinstance(cmds, unicode):
            cmd = cmds

        node = etree.Element(qualify('CLI', BASE_NS_1_0))

        etree.SubElement(node, qualify('Execution',
                                       BASE_NS_1_0)).text = cmd
        if push:
            return self._request(node)
        else:
            return node


class ConfigCommand(RPC):
    def request(self, cmds, push=True):
        """
        Single Configuration element is permitted.
        cmds can be a list or single command
        commands are pushed to the switch in this method
        when push is set to True, otherwise, the element object
        is returned
        """

        if isinstance(cmds, list):
            cmd = '\n'.join(cmds)
        elif isinstance(cmds, str) or isinstance(cmds, unicode):
            cmd = cmds

        node = etree.Element(qualify('CLI', BASE_NS_1_0))

        etree.SubElement(node, qualify('Configuration',
                                       BASE_NS_1_0)).text = cmd
        if push:
            return self._request(node)
        else:
            return node

class Action(RPC):
    def request(self, action=None):
        node = new_ele("action")
        node.append(validated_element(action))
        return self._request(node)
