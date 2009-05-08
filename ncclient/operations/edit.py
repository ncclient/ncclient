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

"""
"""

# NOTES
# - consider class for helping define <config> for EditConfig??


class EditConfig(RPC):
    
    # tested: no
    # combed: no
    
    SPEC = {
        'tag': 'edit-config',
        'subtree': []
    }
    
    def request(self, target=None, target_url=None, config=None,
                default_operation=None, test_option=None, error_option=None):
        util.one_of(target, target_url)
        spec = EditConfig.SPEC.copy()
        subtree = spec['subtree']
        subtree.append({
            'tag': 'target',
            'subtree': util.store_or_url(target, target_url)
            })
        subtree.append({
            'tag': 'config',
            'subtree': config
            })
        if default_operation is not None:
            subtree.append({
                'tag': 'default-operation',
                'text': default_operation
                })
        if test_option is not None:
            self._assert(':validate')
            subtree.append({
                'tag': 'test-option',
                'text': test_option
                })
        if error_option is not None:
            if error_option == 'rollback-on-error':
                self._assert(':rollback-on-error')
            subtree.append({
                'tag': 'error-option',
                'text': error_option
                })


class DeleteConfig(RPC):
    
    # tested: no
    # combed: yes
    
    SPEC = {
        'tag': 'delete-config',
        'subtree': [ { 'tag': 'target', 'subtree': None } ]
    }
    
    def request(self, target=None, target_url=None):
        spec = DeleteConfig.SPEC.copy()
        spec['subtree'][0]['subtree'] = util.store_or_url(target, target_url)
        return self._request(spec)


class CopyConfig(RPC):
    
    # tested: no
    # combed: yes
    
    SPEC = {
        'tag': 'copy-config',
        'subtree': []
    }
    
    def request(self, source=None, source_url=None, target=None, target_url=None):
        spec = CopyConfig.SPEC.copy()
        spec['subtree'].append({
            'tag': 'target',
            'subtree': util.store_or_url(source, source_url)
            })
        spec['subtree'].append({
            'tag': 'target',
            'subtree': util.store_or_url(target, target_url)
            })
        return self._request(spec)


class Validate(RPC):
    
    # tested: no
    # combed: yes
    
    'config attr shd not include <config> root'
    
    DEPENDS = [':validate']
    
    SPEC = {
        'tag': 'validate',
        'subtree': []
    }
    
    def request(self, source=None, config=None):
        util.one_of(source, capability)
        spec = SPEC.copy()
        if source is not None:
            spec['subtree'].append({
                'tag': 'source',
                'subtree': {'tag': source}
            })
        else:
            spec['subtree'].append({
                'tag': 'config',
                'subtree': config
            })
        return self._request(spec)


class Commit(RPC):
    
    # tested: no
    # combed: yes
    
    DEPENDS = [':candidate']
    
    SPEC = { 'tag': 'commit', 'subtree': [] }
    
    def _parse_hook(self):
        pass
    
    def request(self, confirmed=False, timeout=None):
        spec = SPEC.copy()
        if confirmed:
            spec['subtree'].append({'tag': 'confirmed'})
            if timeout is not None:
                spec['subtree'].append({
                    'tag': 'confirm-timeout',
                    'text': timeout
                })
        return self._request(Commit.SPEC)


class ConfirmedCommit(Commit):
    "psuedo-op"
    
    # tested: no
    # combed: yes
    
    DEPENDS = [':candidate', ':confirmed-commit']
    
    def request(self, timeout=None):
        "Commit changes; requireing that a confirming commit follow"
        return Commit.request(self, confirmed=True, timeout=timeout)
    
    def confirm(self):
        "Make the confirming commit"
        return Commit.request(self, confirmed=True)


class DiscardChanges(RPC):
    
    # tested: no
    # combed: yes
    
    DEPENDS = [':candidate']
    
    SPEC = {'tag': 'discard-changes'}
