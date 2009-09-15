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

def connect_ssh(*args, **kwds):
    """Connect to NETCONF server over SSH. See :meth:`SSHSession.connect()
    <ncclient.transport.SSHSession.connect>` for argument details.

    :rtype: :class:`Manager`
    """
    session = transport.SSHSession(capabilities.CAPABILITIES)
    session.load_known_hosts()
    session.connect(*args, **kwds)
    return Manager(session)

#: Same as :meth:`connect_ssh`
connect = connect_ssh

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

class Manager(object):

    """API for NETCONF operations.

    It is also a context manager, so a :class:`Manager` instance can be used
    with the *with* statement. The session is closed when the context ends. """

    def __init__(self, session):
        self._session = session
        self._async_mode = False
        self._timeout = None
        self._raise_mode = 'all'

    def __enter__(self):
        return self

    def __exit__(self, *argss):
        self.close()
        return False

    def __getattr__(self, name):
        op = OPERATIONS.get(name, None)
        if op is None:
            raise AttributeError
        else:
            return op(self.session,
                      async=self._async_mode,
                      timeout=self._timeout,
                      raise_mode=self._raise_mode).request
    
    def locked(self, target):
        """Returns a context manager for the *with* statement.

        :arg target: name of the datastore to lock
        :type target: `string`
        :rtype: :class:`~ncclient.operations.LockContext`
        """
        return operations.LockContext(self._session, target)

    def close(self):
        """Closes the NETCONF session. First does *<close-session>* RPC."""
        try: # try doing it clean
            self._async_mode = False
            self.close_session()
        except Exception as e:
            logger.debug('error doing <close-session> -- %r' % e)
        if self._session.connected: # if that didn't work, this sure will :)
            self._session.close()

    @property
    def session(self):
        ":class:`~ncclient.transport.Session` instance"
        return self._session

    @property
    def client_capabilities(self):
        ":class:`~ncclient.capabilities.Capabilities` object for client"
        return self._session._client_capabilities

    @property
    def server_capabilities(self):
        ":class:`~ncclient.capabilities.Capabilities` object for server"
        return self._session._server_capabilities

    @property
    def session_id(self):
        "*<session-id>* as assigned by NETCONF server"
        return self._session.id

    @property
    def connected(self):
        "Whether currently connected to NETCONF server"
        return self._session.connected

    def set_async_mode(self, bool=True):
        self._async_mode = bool

    def set_raise_mode(self, mode):
        assert(choice in ('all', 'errors', 'none'))
        self._raise_mode = mode

    async_mode = property(fget=lambda self: self._async_mode, fset=set_async_mode)

    raise_mode = property(fget=set_raise_mode, fset=set_raise_mode)
