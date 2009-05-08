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

from ncclient.rpc import RPC, RPCReply

import util

class GetReply(RPCReply):
    
    # tested: no
    
    def __init__(self, *args, **kwds):
        RPCReply.__init__(self, *args, **kwds)
        self._data = None
    
    def parse(self):
        RPCReply.parse(self)
        if self.ok:
            self.root.find('data')
    
    @property
    def data(self):
        return ET.tostring(self._data)

class Get(RPC):
    
    # tested: no
    
    SPEC = {
        'tag': 'get',
        'subtree': []
    }
    
    REPLY_CLS = GetReply
    
    def request(self, filter=None):
        spec = Get.SPEC.copy()
        if filter is not None:
            spec['subtree'].append(util.build_filter(*filter))
        return self._request(spec)

class GetConfig(RPC):
    
    SPEC = {
        'tag': 'get-config',
        'subtree': []
    }
    
    REPLY_CLS = GetReply
    
    def request(self, source=None, source_url=None, filter=None):
        util.one_of(source, source_url)
        spec = GetConfig.SPEC.copy()
        subtree = spec['subtree']
        subtree.append({'tag': 'source', 'subtree': util.store_or_url(source, source_url)})
        if filter is not None:
            subtree.append(util.build_filter(*filter))
        return self._request(spec)
