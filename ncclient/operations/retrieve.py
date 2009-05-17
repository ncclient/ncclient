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

    # TESTED

    """Adds attributes for the *<data>* element to :class:`RPCReply`, which
    pertains to the :class:`Get` and :class:`GetConfig` operations."""

    def _parsing_hook(self, root):
        self._data = None
        if not self._errors:
            self._data = content.find(root, 'data',
                                      nslist=[content.BASE_NS,
                                              content.CISCO_BS])

    @property
    def data_ele(self):
        "*<data>* element as an :class:`~xml.etree.ElementTree.Element`"
        if not self._parsed:
            self.parse()
        return self._data

    @property
    def data_xml(self):
        "*<data>* element as an XML string"
        if not self._parsed:
            self.parse()
        return content.ele2xml(self._data)

    @property
    def data_dtree(self):
        "*<data>* element in :ref:`dtree`"
        return content.ele2dtree(self._data)

    #: Same as :attr:`data_ele`
    data = data_ele


class Get(RPC):

    # TESTED

    "The *<get>* RPC"

    SPEC = {'tag': 'get', 'subtree': []}

    REPLY_CLS = GetReply

    def request(self, filter=None):
        """
        :arg filter: optional; see :ref:`filter`

        :seealso: :ref:`return`
        """
        spec = Get.SPEC.copy()
        if filter is not None:
            spec['subtree'].append(util.build_filter(filter))
        return self._request(spec)


class GetConfig(RPC):

    # TESTED

    "The *<get-config>* RPC"

    SPEC = {'tag': 'get-config', 'subtree': []}

    REPLY_CLS = GetReply

    def request(self, source, filter=None):
        """
        :arg source: See :ref:`source_target`

        :arg filter: optional; see :ref:`filter`

        :seealso: :ref:`return`
        """
        spec = GetConfig.SPEC.copy()
        spec['subtree'].append(util.store_or_url('source', source, self._assert))
        if filter is not None:
            spec['subtree'].append(util.build_filter(filter))
        return self._request(spec)
