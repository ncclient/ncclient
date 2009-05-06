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

from ncclient.capabilities import URI
from ncclient.rpc import RPC

import util

class EditConfig(RPC):
    
    SPEC = {
        'tag': 'edit-config',
        'children': [
            { 'target': None }
        ]
    }
    
    def request(self):
        pass


class DeleteConfig(RPC): # x
    
    SPEC = {
        'tag': 'delete-config',
        'children': [ { 'tag': 'target', 'children': None } ]
    }
    
    def request(self, target=None, target_url=None):
        spec = DeleteConfig.SPEC.copy()
        spec['children'][0]['children'] = util.store_or_url(target, target_url)
        return self._request(spec)


class CopyConfig(RPC): # x
    
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


class Validate(RPC): # xxxxx
    
    DEPENDS = [':validate']
    
    SPEC = {
        'tag': 'validate',
        'children': []
    }
    
    def request(self, source=None, config=None):
        #self.either_or(source, config)
        #
        #if source is None and config is None:
        #    raise OperationError('Insufficient parameters')
        #if source is not None and config is not None:
        #    raise OperationError('Too many parameters')
        #spec = Validate.SPEC.copy()
        #
        util.one_of(source, capability)
        if source is not None:
            spec['children'].append({
                'tag': 'source',
                'children': {'tag': source}
                })
        #
        #else:
        #    if isinstance(config, dict):
        #        if config['tag'] != 'config':
        #            child['tag'] = 'config'
        #            child['children'] = config
        #        else:
        #            child = config
        #    elif isinstance(config, Element):
        #        pass
        #    else:
        #        from xml.etree import cElementTree as ET
        #        ele = ET.XML(unicode(config))
        #        if __(ele.tag) != 'config':
        #            pass
        #        else:
        #            pass
        #    spec['children'].append(child)
        #
        return self._request(spec)

class Commit(RPC): # x
    
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


class DiscardChanges(RPC): # x
    
    DEPENDS = [':candidate']
    
    SPEC = {'tag': 'discard-changes'}
    
    def request(self):
        return self._request(DiscardChanges.SPEC)
