from ncclient.xml_ import *

from ncclient.operations.rpc import RPC
from ncclient.operations.rpc import RPCReply
from ncclient.operations.rpc import RPCError
from ncclient import NCClientError

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

class Commit(RPC):
    "`commit` RPC. Depends on the `:candidate` capability, and the `:confirmed-commit`."

    DEPENDS = [':candidate']

    def request(self, confirmed=False, timeout=None, comment=None, synchronize=False, at_time=None):
        """Commit the candidate configuration as the device's new current configuration. Depends on the `:candidate` capability.

        A confirmed commit (i.e. if *confirmed* is `True`) is reverted if there is no followup commit within the *timeout* interval. If no timeout is specified the confirm timeout defaults to 600 seconds (10 minutes). A confirming commit may have the *confirmed* parameter but this is not required. Depends on the `:confirmed-commit` capability.

        *confirmed* whether this is a confirmed commit. Mutually exclusive with at_time.

        *timeout* specifies the confirm timeout in seconds

        *comment* a string to comment the commit with. Review on the device using 'show system commit'

        *synchronize* Whether we should synch this commit across both Routing Engines

        *at_time* Mutually exclusive with confirmed. The time at which the commit should happen. Junos expects either of these two formats:
            A time value of the form hh:mm[:ss] (hours, minutes, and, optionally, seconds)
            A date and time value of the form yyyy-mm-dd hh:mm[:ss] (year, month, date, hours, minutes, and, optionally, seconds)"""
        node = new_ele("commit")
        if confirmed and at_time is not None:
            raise NCClientError("'Commit confirmed' and 'commit at' are mutually exclusive.")
        if confirmed:
            self._assert(":confirmed-commit")
            sub_ele(node, "confirmed")
            if timeout is not None:
                sub_ele(node, "confirm-timeout").text = timeout
        elif at_time is not None:
            sub_ele(node, "at-time").text = at_time
        if comment is not None:
            sub_ele(node, "log").text = comment
        if synchronize:
            sub_ele(node, "synchronize")
        return self._request(node)
