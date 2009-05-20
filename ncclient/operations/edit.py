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

from ncclient import content

from rpc import RPC

import util

import logging
logger = logging.getLogger('ncclient.operations.edit')



"Operations related to changing device configuration"

class EditConfig(RPC):

    # TESTED

    "*<edit-config>* RPC"

    SPEC = {'tag': 'edit-config', 'subtree': []}

    def request(self, target, config, default_operation=None, test_option=None,
                error_option=None):
        """
        :arg target: see :ref:`source_target`
        :type target: string

        :arg config: a config element in :ref:`dtree`
        :type config: `string` or `dict` or :class:`~xml.etree.ElementTree.Element`

        :arg default_operation: optional; one of {'merge', 'replace', 'none'}
        :type default_operation: `string`

        :arg error_option: optional; one of {'stop-on-error', 'continue-on-error', 'rollback-on-error'}. Last option depends on the *:rollback-on-error* capability
        :type error_option: string

        :arg test_option: optional; one of {'test-then-set', 'set'}. Depends on *:validate* capability.
        :type test_option: string

        :seealso: :ref:`return`
        """
        spec = deepcopy(EditConfig.SPEC)
        subtree = spec['subtree']
        subtree.append(util.store_or_url('target', target, self._assert))
        if error_option is not None:
            if error_option == 'rollback-on-error':
                self._assert(':rollback-on-error')
            subtree.append({
                'tag': 'error-option',
                'text': error_option
                })
        if test_option is not None:
            self._assert(':validate')
            subtree.append({
                'tag': 'test-option',
                'text': test_option
                })
        if default_operation is not None:
            subtree.append({
                'tag': 'default-operation',
                'text': default_operation
                })
        subtree.append(content.validated_element(config, ('config', content.qualify('config'))))
        return self._request(spec)

class DeleteConfig(RPC):

    # TESTED

    "*<delete-config>* RPC"

    SPEC = {'tag': 'delete-config', 'subtree': []}

    def request(self, target):
        """
        :arg target: See :ref:`source_target`
        :type target: `string` or `dict` or :class:`~xml.etree.ElementTree.Element`

        :seealso: :ref:`return`
        """
        spec = deepcopy(DeleteConfig.SPEC)
        spec['subtree'].append(util.store_or_url('target', target, self._assert))
        return self._request(spec)


class CopyConfig(RPC):

    # TESTED

    "*<copy-config>* RPC"

    SPEC = {'tag': 'copy-config', 'subtree': []}

    def request(self, source, target):
        """
        :arg source: See :ref:`source_target`
        :type source: `string` or `dict` or :class:`~xml.etree.ElementTree.Element`

        :arg target: See :ref:`source_target`
        :type target: `string` or `dict` or :class:`~xml.etree.ElementTree.Element`

        :seealso: :ref:`return`
        """
        spec = deepcopy(CopyConfig.SPEC)
        spec['subtree'].append(util.store_or_url('target', target, self._assert))
        spec['subtree'].append(util.store_or_url('source', source, self._assert))
        return self._request(spec)


class Validate(RPC):

    # TESTED

    "*<validate>* RPC. Depends on the *:validate* capability."

    DEPENDS = [':validate']

    SPEC = {'tag': 'validate', 'subtree': []}

    def request(self, source):
        """
        :arg source: See :ref:`source_target`
        :type source: `string` or `dict` or :class:`~xml.etree.ElementTree.Element`

        :seealso: :ref:`return`
        """
        spec = deepcopy(Validate.SPEC)
        try:
            src = content.validated_element(source, ('config', content.qualify('config')))
        except Exception as e:
            logger.debug(e)
            src = util.store_or_url('source', source, self._assert)
        spec['subtree'].append({
            'tag': 'source',
            'subtree': src
            })
        return self._request(spec)


class Commit(RPC):

    # TESTED

    "*<commit>* RPC. Depends on the *:candidate* capability."

    DEPENDS = [':candidate']

    SPEC = {'tag': 'commit', 'subtree': []}

    def _parse_hook(self):
        pass

    def request(self, confirmed=False, timeout=None):
        """
        Requires *:confirmed-commit* capability if *confirmed* argument is
        :const:`True`.

        :arg confirmed: optional; request a confirmed commit
        :type confirmed: `bool`

        :arg timeout: specify timeout for confirmed commit
        :type timeout: `int`

        :seealso: :ref:`return`
        """
        spec = deepcopy(Commit.SPEC)
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

    # TESTED

    "*<discard-changes>* RPC. Depends on the *:candidate* capability."

    DEPENDS = [':candidate']

    SPEC = {'tag': 'discard-changes'}

    def request(self):
        ":seealso: :ref:`return`"
        return self._request(DiscardChanges.SPEC)
