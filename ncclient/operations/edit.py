# Copyright 2009 Shikhar Bhushan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ncclient.xml_ import *

from rpc import RPC

import util

import logging
logger = logging.getLogger("ncclient.operations.edit")

"Operations related to changing device configuration"

class EditConfig(RPC):

    "*<edit-config>* RPC"
    
    def request(self, target, config, default_operation=None, test_option=None,
                error_option=None):
        node = new_ele("edit-config")
        node.append(util.datastore_or_url("target", target, self._assert))
        if error_option is not None:
            if error_option == "rollback-on-error":
                self._assert(":rollback-on-error")
            sub_ele(node, "error-option").text = error_option
        if test_option is not None:
            self._assert(':validate')
            sub_ele(node, "test-option").text = test_option
        if default_operation is not None:
            # TODO: check if it is a valid default-operation
            sub_ele(node, "default-operation").text = default_operation
        node.append(validated_element(config, ("config", qualify("config"))))
        return self._request(node)


class DeleteConfig(RPC):

    "*<delete-config>* RPC"

    def request(self, target):
        node = new_ele("delete-config")
        node.append(util.datastore_or_url("target", target, self._assert))
        return self._request(node)


class CopyConfig(RPC):

    "*<copy-config>* RPC"
    
    def request(self, source, target):
        node = new_ele("copy-config")
        node.append(util.datastore_or_url("target", target, self._assert))
        node.append(util.datastore_or_url("source", source, self._assert))
        return self._request(node)


class Validate(RPC):

    "*<validate>* RPC. Depends on the *:validate* capability."

    DEPENDS = [':validate']

    def request(self, source):
        node = new_ele("validate")
        try:
            src = validated_element(source, ("config", qualify("config")))
        except Exception as e:
            logger.debug(e)
            src = util.datastore_or_url("source", source, self._assert)
        (node if src.tag == "source" else sub_ele(node, "source")).append(src)
        return self._request(node)


class Commit(RPC):

    "*<commit>* RPC. Depends on the *:candidate* capability, and the *:confirmed-commit* "

    DEPENDS = [':candidate']
    
    def request(self, confirmed=False, timeout=None):
        node = new_ele("commit")
        if confirmed:
            self._assert(":confirmed-commit")
            sub_ele(node, "confirmed")
            if timeout is not None:
                # TODO check if timeout is a valid integer?
                sub_ele(node, "confirm-timeout").text = timeout
        return self._request(node)


class DiscardChanges(RPC):

    "*<discard-changes>* RPC. Depends on the *:candidate* capability."

    DEPENDS = [":candidate"]

    def request(self):
        return self._request(new_ele("discard-changes"))