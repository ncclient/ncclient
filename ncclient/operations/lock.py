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

from rpc import RPC


class Lock(RPC):
    
    def __init__(self, session):
        RPC.__init__(self, session)
        self.spec = {
            'tag': 'lock',
            'children': { 'tag': 'target', 'children': {'tag': None} }
            }
    
    def request(self, target='running', reply_event=None):
        self.spec['children']['children']['tag'] = target
        self._do_request(self.spec, reply_event)


class Unlock(RPC):
    
    def __init__(self, session):
        RPC.__init__(self, session)
        self.spec = {
            'tag': 'unlock',
            'children': { 'tag': 'target', 'children': {'tag': None} }
            }
    
    def request(self, target='running', reply_event=None):
        self.spec['children']['children']['tag'] = target
        self._do_request(self.spec, reply_event)
