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

'Locking-related NETCONF operations'

from copy import deepcopy

from ncclient.rpc import RPC

# TODO - a context manager around some <target> would be real neat

class Lock(RPC):
    
    SPEC = {
        'tag': 'lock',
        'children': {
            'tag': 'target',
            'children': {'tag': None }
        }
    }
    
    def request(self, target='running'):
        spec = deepcopy(Lock.SPEC)
        spec['children']['children']['tag'] = target
        return self._request(spec)


class Unlock(RPC):
    
    SPEC = {
        'tag': 'unlock',
        'children': {
            'tag': 'target',
            'children': {'tag': None }
        }
    }
    
    def request(self, target='running'):
        spec = deepcopy(Unlock.SPEC)
        spec['children']['children']['tag'] = target
        return self._request(self.spec)
