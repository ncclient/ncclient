#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by yangxufeng.zhao

from ncclient.xml_ import *

from ncclient.operations.rpc import RPC


class CLI(RPC):
    def request(self, command=None):
        """command text
        view: Execution user view exec
              Configuration system view exec
        """
        # node = new_ele("execute-cli")
        node = new_ele("execute-cli", attrs={"xmlns":HW_PRIVATE_NS})
        node.append(validated_element(command))
        return self._request(node)


class Action(RPC):
    "`execute-action` RPC"
    def request(self, action=None):
        node = new_ele("execute-action", attrs={"xmlns":HW_PRIVATE_NS})
        node.append(validated_element(action))
        return self._request(node)


class GetNext(RPC):
    """"`get-next` RPC.
    When the <get> operation is performed to query mass running data,
    the device divides returned data into multiple packets. When the first
    packet is returned, the NETCONF client executes the <get-next> operation
    to request the next packet or terminate data query.

    If a <rpc-replay> message contains set-id="**" (** is an integer),
    the message has been divided into multiple packets.
    The client executes <get-next> to obtain the next packet.
    This operation repeats until the <rpc-replay> message does not contain
    set-id="**".
    """
    def request(self, set_id=None, discard=None):
        node = new_ele("get-next",
                       attrs={"xmlns": HW_PRIVATE_NS, "set-id": str(set_id)})
        if discard:
            node.append(validated_element("<discard/>"))
        return self._request(node)
