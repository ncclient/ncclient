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

def build_filter(spec, type, criteria):
    filter = {
        'tag': 'filter',
        'attributes': {'type': type}
    }
    if type == 'subtree':
        filter['children'] = [criteria]
    elif type == 'xpath':
        filter['attributes']['select'] = criteria
    return filter

class Get(RPC): # xx
    
    SPEC = {
        'tag': 'get',
        'children': []
    }
    
    REPLY_CLS = GetReply
    
    def request(self, filter=None):
        spec = Get.SPEC.copy()
        if filter is not None:
            #if filter[0] == 'xpath':
            #    self._assert(':xpath')
            spec['children'].append(build_filter(*filter))
        return self._request(spec)

class GetReply(RPCReply):
    
    def parse(self):
        RPCReply.parse(self)

class GetConfig(RPC): # xx
    
    SPEC = {
        'tag': 'get-config',
        'children': [ { 'tag': 'source', 'children': {'tag': None } } ]
    }
    
    REPLY_CLS = GetConfigReply
    
    def request(self, source=None, source_url=None, filter=None):
        self._one_of(source, source_url)
        spec = GetConfig.SPEC.copy()
        if source is not None:
            spec['children'][0]['children']['tag'] = source
        if source_url is not None:
            #self._assert(':url')
            spec['children'][0]['children']['tag'] = 'url'
            spec['children'][0]['children']['text'] = source_url        
        if filter is not None:
            #if filter[0] == 'xpath':
            #    self._assert(':xpath')
            spec['children'].append(build_filter(*filter))
        return self._request(spec)

class GetReply(RPCReply):
    
    def parse(self):
        RPCReply.parse(self)
