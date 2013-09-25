from ncclient.xml_ import *

from ncclient.operations.rpc import RPC
from ncclient.operations.rpc import RPCReply
from ncclient.operations.rpc import RPCError

class GetConfiguration(RPC):
    def request(self, format='xml', filter=None):
        node = new_ele('get-configuration', {'format':format})
        if filter is not None:
            node.append(filter)
        return self._request(node)

class LoadConfiguration(RPC):
    def request(self, format='xml', action='merge',
            target='candidate', config=None):
        if config is not None:
            if type(config) == list:
                config = '\n'.join(config)
            if action == 'set':
                format = 'text'
            node = new_ele('load-configuration', {'action':action, 'format':format})
            if format == 'xml':
                config_node = sub_ele(node, 'configuration')
                config_node.append(config)
            if format == 'text' and not action == 'set':
                config_node = sub_ele(node, 'configuration-text').text = config
            if action == 'set' and format == 'text':
                config_node = sub_ele(node, 'configuration-set').text = config
            return self._request(node)

class CompareConfiguration(RPC):
    def request(self, rollback=0):
        node = new_ele('get-configuration', {'compare':'rollback', 'rollback':str(rollback)})
        return self._request(node)

class ExecuteRpc(RPC):
    def request(self, rpc):
        if isinstance(rpc, str):
            rpc = to_ele(rpc)
        return self._request(rpc)

class Command(RPC):
    def request(self, command=None, format='xml'):
        node = new_ele('command', {'format':format})
        node.text = command
        return self._request(node)

class Reboot(RPC):
    def request(self):
        node = new_ele('request-reboot')
        return self._request(node)

class Halt(RPC):
    def request(self):
        node = new_ele('request-halt')
        return self._request(node)
