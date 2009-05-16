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

from rpc import RPC, RPCReply

from ncclient import content

import util

class GetReply(RPCReply):

    """Adds attributes for the *<data>* element to :class:`RPCReply`, pertinent
    to the *<get>* or *<get-config>* operations."""

    def _parsing_hook(self, root):
        self._data = None
        if not self._errors:
            self._data = content.find(root, 'data',
                                      nslist=[content.BASE_NS,
                                              content.CISCO_BS])

    @property
    def data_ele(self):
        "As an :class:`~xml.etree.ElementTree.Element`"
        if not self._parsed:
            self.parse()
        return self._data

    @property
    def data_xml(self):
        "As an XML string"
        if not self._parsed:
            self.parse()
        return content.ele2xml(self._data)

    data = data_ele


class Get(RPC):

    "*<get>* RPC"

    SPEC = {
        'tag': 'get',
        'subtree': []
    }

    REPLY_CLS = GetReply

    def request(self, filter=None):
        spec = Get.SPEC.copy()
        if filter is not None:
            spec['subtree'].append(util.build_filter(filter))
        return self._request(spec)


class GetConfig(RPC):

    "*<get-config>* RPC"

    SPEC = {
        'tag': 'get-config',
        'subtree': []
    }

    REPLY_CLS = GetReply

    def request(self, source, filter=None):
        spec = GetConfig.SPEC.copy()
        spec['subtree'].append(util.store_or_url('source', source, self._assert))
        if filter is not None:
            spec['subtree'].append(util.build_filter(filter))
        return self._request(spec)
