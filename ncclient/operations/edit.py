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

from ncclient import content

from rpc import RPC

import util

"Operations related to configuration editing"

class EditConfig(RPC):

    SPEC = {'tag': 'edit-config', 'subtree': []}

    def request(self, target=None, config=None, default_operation=None,
                test_option=None, error_option=None):
        util.one_of(target, config)
        spec = EditConfig.SPEC.copy()
        subtree = spec['subtree']
        subtree.append(util.store_or_url('target', target, self._assert))
        subtree.append(content.validated_root(config, 'config'))
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
        return self._request(spec)


class DeleteConfig(RPC):

    SPEC = {'tag': 'delete-config', 'subtree': []}

    def request(self, target):
        spec = DeleteConfig.SPEC.copy()
        spec['subtree'].append(util.store_or_url('target', target, self._assert))
        return self._request(spec)


class CopyConfig(RPC):

    SPEC = {'tag': 'copy-config', 'subtree': []}

    def request(self, source, target):
        spec = CopyConfig.SPEC.copy()
        spec['subtree'].append(util.store_or_url('source', source, self._assert))
        spec['subtree'].append(util.store_or_url('target', target, self._assert))
        return self._request(spec)


class Validate(RPC):

    DEPENDS = [':validate']

    SPEC = {'tag': 'validate', 'subtree': []}

    def request(self, source):
        # determine if source is a <config> element
        spec = Validate.SPEC.copy()
        try:
            spec['subtree'].append({
                'tag': 'source',
                'subtree': content.validated_root(config, ('config', content.qualify('config')))
                })
        except ContentError:
            spec['subtree'].append(util.store_or_url('source', source, self._assert))
        return self._request(spec)


class Commit(RPC):

    DEPENDS = [':candidate']

    SPEC = {'tag': 'commit', 'subtree': []}

    def _parse_hook(self):
        pass

    def request(self, confirmed=False):
        spec = SPEC.copy()
        if confirmed:
            self._assert(':confirmed-commit')
            spec['subtree'].append({'tag': 'confirmed'})
            if timeout is not None:
                spec['subtree'].append({
                    'tag': 'confirm-timeout',
                    'text': timeout
                })
        return self._request(Commit.SPEC)


class DiscardChanges(RPC):

    DEPENDS = [':candidate']

    SPEC = {'tag': 'discard-changes'}


class ConfirmedCommit(Commit):
    "psuedo-op"

    DEPENDS = [':candidate', ':confirmed-commit']

    def request(self):
        "Commit changes requiring that a confirm/discard follow"
        return Commit.request(self, confirmed=True)

    def confirm(self):
        "Confirm changes"
        return Commit.request(self, confirmed=True)

    def discard(self):
        "Discard changes"
        return DiscardChanges(self.session, self.async, self.timeout).request()
