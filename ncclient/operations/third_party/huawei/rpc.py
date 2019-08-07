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


class Update(RPC):
    """
    update configure or update candidate DB to running DB.
    """
    def request(self, candidate=True):
        if candidate:
            node = new_ele("commit")
            update = new_ele("update-candidate", attrs={"xmlns":HW_PRIVATE_NS})
            node.append(update)
        else:
            node = new_ele("update ", attrs={"xmlns":HW_PRIVATE_NS})
        return self._request(node)
