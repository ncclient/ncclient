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
    
    'Adds data attribute'
    
    # tested: no
    # combed: yes
    
    def _parsing_hook(self, root):
        self._data = None
        if not self._errors:
            self._data = content.find(root, 'data', strict=False)
    
    @property
    def data(self):
        if not self._parsed:
            self.parse()
        return self._data

class Get(RPC):
    
    # tested: no
    # combed: yes
    
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

    # tested: no
    # combed: yes
    
    SPEC = {
        'tag': 'get-config',
        'subtree': []
    }
    
    REPLY_CLS = GetReply
    
    def request(self, source, filter=None):
        """
        `filter` has to be a tuple of (type, criteria)
        The type may be one of 'xpath' or 'subtree'
        The criteria may be an ElementTree.Element, an XML fragment, or tree specification
        """
        spec = GetConfig.SPEC.copy()
        spec['subtree'].append(util.store_or_url('source', source, self._assert))
        if filter is not None:
            spec['subtree'].append(util.build_filter(filter))
        return self._request(spec)
