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

from copy import deepcopy

from ncclient.rpc import RPC

def build_filter(spec, type, criteria):
    filter = {
        'tag': 'filter',
        'attributes': {'type': type}
    }
    if type=='subtree':
        if isinstance(criteria, dict):
            filter['children'] = [criteria]
        else:
            filter['text'] = criteria
    elif type=='xpath':
        filter['attributes']['select'] = criteria

class Get(RPC):
    
    SPEC = {
        'tag': 'get',
        'children': []
    }
    
    def request(self, filter=None):
        spec = deepcopy(SPEC)
        if filter is not None:
            spec['children'].append(build_filter(*filter))
        return self._request(spec)


class GetConfig(RPC):
    
    SPEC = {
        'tag': 'get-config',
        'children': [ { 'tag': 'source', 'children': {'tag': None } } ]
    }
    
    def request(self, source='running', filter=None):
        spec = deepcopy(SPEC)
        spec['children'][0]['children']['tag'] = source
        if filter is not None:
            spec['children'].append(build_filter(*filter))
        return self._request(spec)
