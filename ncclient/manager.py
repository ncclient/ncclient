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

"Thin layer of abstraction around NCClient"

import capabilities
import operations
import transport

import logging
logger = logging.getLogger('ncclient.manager')


#: :class:`Capabilities` object representing the capabilities currently supported by NCClient
CAPABILITIES = capabilities.Capabilities([
    "urn:ietf:params:netconf:base:1.0",
    "urn:ietf:params:netconf:capability:writable-running:1.0",
    "urn:ietf:params:netconf:capability:candidate:1.0",
    "urn:ietf:params:netconf:capability:confirmed-commit:1.0",
    "urn:ietf:params:netconf:capability:rollback-on-error:1.0",
    "urn:ietf:params:netconf:capability:startup:1.0",
    "urn:ietf:params:netconf:capability:url:1.0?scheme=http,ftp,file,https,sftp",
    "urn:ietf:params:netconf:capability:validate:1.0",
    "urn:ietf:params:netconf:capability:xpath:1.0",
    "urn:liberouter:params:netconf:capability:power-control:1.0"
    "urn:ietf:params:netconf:capability:interleave:1.0"
    #'urn:ietf:params:netconf:capability:notification:1.0', # TODO    
])


OPERATIONS = {
    "get": operations.Get,
    "get_config": operations.GetConfig,
    "edit_config": operations.EditConfig,
    "copy_config": operations.CopyConfig,
    "validate": operations.Validate,
    "commit": operations.Commit,
    "discard_changes": operations.DiscardChanges,
    "delete_config": operations.DeleteConfig,
    "lock": operations.Lock,
    "unlock": operations.Unlock,
    "close_session": operations.CloseSession,
    "kill_session": operations.KillSession,
    "poweroff_machine": operations.PoweroffMachine,
    "reboot_machine": operations.RebootMachine
}


def connect_ssh(*args, **kwds):
    session = transport.SSHSession(CAPABILITIES)
    session.load_known_hosts()
    session.connect(*args, **kwds)
    return Manager(session)

#: Same as :meth:`connect_ssh`
connect = connect_ssh


class Manager(object):

    def __init__(self, session):
        self._session = session
        self._async_mode = False
        self._timeout = None
        self._raise_mode = 'all'

    def __enter__(self):
        return self

    def __exit__(self, *argss):
        self.close_session()
        return False

    def __getattr__(self, name):
        op = OPERATIONS.get(name, None)
        if op is None:
            raise AttributeError
        else:
            return op(self._session,
                      async=self._async_mode,
                      timeout=self._timeout,
                      raise_mode=self._raise_mode).request
    
    def locked(self, target):
        return operations.LockContext(self._session, target)
    
    @property
    def client_capabilities(self):
        return self._session._client_capabilities

    @property
    def server_capabilities(self):
        return self._session._server_capabilities

    @property
    def session_id(self):
        return self._session.id

    @property
    def connected(self):
        return self._session.connected

    def set_async_mode(self, mode):
        self._async_mode = mode

    def set_raise_mode(self, mode):
        assert(choice in ("all", "errors", "none"))
        self._raise_mode = mode

    async_mode = property(fget=lambda self: self._async_mode, fset=set_async_mode)

    raise_mode = property(fget=lambda self: self._raise_mode, fset=set_raise_mode)
