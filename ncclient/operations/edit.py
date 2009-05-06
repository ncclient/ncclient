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
from ncclient.content import iselement

import util

class EditConfig(RPC):
    
    SPEC = {
        'tag': 'edit-config',
        'children': [ ]
    }
    
    def request(self, target=None, target_url=None, config=None,
                default_operation=None, test_option=None, error_option=None):
        util.one_of(target, target_url)
        spec = EditConfig.SPEC.copy()
        params = spec['children']
        params.append({'tag': 'target', 'children': util.store_or_url(target, target_url)})
        params.append({'tag': 'config', 'children': config})
        if default_operation is not None:
            params.append({'tag': 'default-operation', 'text': default_operation})
        if test_option is not None:
            params.append({'tag': 'test-option', 'text': test_option})
        if error_option is not None:
            params.append({'tag': 'test-option', 'text': test_option})

class DeleteConfig(RPC):
    
    SPEC = {
        'tag': 'delete-config',
        'children': [ { 'tag': 'target', 'children': None } ]
    }
    
    def request(self, target=None, target_url=None):
        spec = DeleteConfig.SPEC.copy()
        spec['children'][0]['children'] = util.store_or_url(target, target_url)
        return self._request(spec)


class CopyConfig(RPC):
    
    SPEC = {
        'tag': 'copy-config',
        'children': [
            { 'tag': 'source', 'children': {'tag': None } },
            { 'tag': 'target', 'children': {'tag': None } }
        ]
    }
    
    def request(self, source=None, source_url=None, target=None, target_url=None):
        spec = CopyConfig.SPEC.copy()
        spec['children'][0]['children'] = util.store_or_url(source, source_url)
        spec['children'][1]['children'] = util.store_or_url(target, target_url)
        return self._request(spec)


class Validate(RPC):
    
    'config attr shd not include <config> root'
    
    DEPENDS = [':validate']
    
    SPEC = {
        'tag': 'validate',
        'children': []
    }
    
    def request(self, source=None, config=None):
        util.one_of(source, capability)
        spec = SPEC.copy()
        if source is not None:
            spec['children'].append({
                'tag': 'source', 'children': {'tag': source}
                })
        else:
            spec['children'].append({'tag': 'config', 'children': config})
        return self._request(spec)


class Commit(RPC):
    
    DEPENDS = [':candidate']
    
    SPEC = {'tag': 'commit', 'children': [] }
    
    def _parse_hook(self):
        pass
    
    def request(self, confirmed=False, timeout=None):
        spec = SPEC.copy()
        if confirmed:
            self._assert(':confirmed-commit')
            children = spec['children']
            children.append({'tag': 'confirmed'})
            if timeout is not None:
                children.append({
                    'tag': 'confirm-timeout',
                    'text': timeout
                })
        return self._request(Commit.SPEC)


class DiscardChanges(RPC):
    
    DEPENDS = [':candidate']
    
    SPEC = {'tag': 'discard-changes'}
    
    request = lambda self: self._request(DiscardChanges.SPEC)
