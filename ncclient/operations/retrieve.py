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
    
    def parse(self):
        RPCReply.parse(self)
    
    @property
    def data(self):
        return None

class Get(RPC):
    
    SPEC = {
        'tag': 'get',
        'children': []
    }
    
    REPLY_CLS = GetReply
    
    def request(self, filter=None):
        spec = Get.SPEC.copy()
        if filter is not None:
            spec['children'].append(util.build_filter(*filter))
        return self._request(spec)

class GetConfig(RPC):
    
    SPEC = {
        'tag': 'get-config',
        'children': []
    }
    
    REPLY_CLS = GetReply
    
    def request(self, source=None, source_url=None, filter=None):
        util.one_of(source, source_url)
        spec = GetConfig.SPEC.copy()
        children = spec['children']
        children.append({'tag': 'source', 'children': util.store_or_url(source, source_url)})
        if filter is not None:
            children.append(util.build_filter(*filter))
        return self._request(spec)
