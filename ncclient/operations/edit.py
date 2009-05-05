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

from ncclient.rpc import RPC

# TODO


'''
notes
-> editconfig and copyconfig <running> target depends on :writable-running
-> 

'''

class EditConfig(RPC):
    
    SPEC = {
        'tag': 'edit-config',
        'children': [
            { 'target': None }
        ]
    }
    
    def request(self):
        pass

class CopyConfig(RPC):
    
    SPEC = {
        
    }
    
    def request(self):
        pass

class DeleteConfig(RPC):
    
    SPEC = {
        'tag': 'delete-config',
        'children': [
            'tag': 'target',
            'children': {'tag': None }
        ]
    }
    
    def request(self, target=None, targeturl=None):
        spec = deepcopy(DeleteConfig.SPEC)
        

class Validate(RPC):
    
    DEPENDS = ['urn:ietf:params:netconf:capability:validate:1.0']
    SPEC = {}
    
    def request(self):
        pass


class Commit(RPC):
    
    SPEC = {'tag': 'commit'}
    
    def request(self):
        return self._request(Commit.SPEC)


class DiscardChanges(RPC):
    
    DEPENDS = ['urn:ietf:params:netconf:capability:candidate:1.0']
    SPEC = {'tag': 'discard-changes'}
    
    def request(self):
        return self._request(DiscardChanges.SPEC)
