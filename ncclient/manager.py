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
    <ncclient.transport.SSHSession.connect>` for function signature."""
    session = transport.SSHSession(capabilities.CAPABILITIES)
    session.load_known_hosts()
    session.connect(*args, **kwds)
    return Manager(session)

#: Same as :meth:`connect_ssh`
connect = connect_ssh

#: Raise all :class:`~ncclient.operations.rpc.RPCError`
RAISE_ALL = 0
#: Only raise when *error-severity* is "error" i.e. no warnings
RAISE_ERR = 1
#: Don't raise any
RAISE_NONE = 2

class Manager:

    """API for NETCONF operations. Currently only supports making synchronous
    RPC requests.

    It is also a context manager, so a :class:`Manager` instance can be used
    with the *with* statement. The session is closed when the context ends. """

    def __init__(self, session):
        self._session = session
        self._raise = RAISE_ALL

    def set_rpc_error_action(self, action):
        """Specify the action to take when an *<rpc-error>* element is encountered.

        :arg action: one of :attr:`RAISE_ALL`, :attr:`RAISE_ERR`, :attr:`RAISE_NONE`
        """
        self._raise = action

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False

    def do(self, op, *args, **kwds):
        op = operations.OPERATIONS[op](self._session)
        reply = op.request(*args, **kwds)
        if not reply.ok:
            if self._raise == RAISE_ALL:
                raise reply.error
            elif self._raise == RAISE_ERROR:
                for error in reply.errors:
                    if error.severity == 'error':
                        raise error
        return reply

    #: :see: :meth:`Get.request() <ncclient.operations.Get.request>`
    get = lambda self, *args, **kwds: self.do('get', *args, **kwds)

    #: :see: :meth:`GetConfig.request() <ncclient.operations.GetConfig.request>`
    get_config = lambda self, *args, **kwds: self.do('get-config', *args, **kwds)

    #: :see: :meth:`EditConfig.request() <ncclient.operations.EditConfig.request>`
    edit_config = lambda self, *args, **kwds: self.do('edit-config', *args, **kwds)

    #: :see: :meth:`CopyConfig.request() <ncclient.operations.CopyConfig.request>`
    copy_config = lambda self, *args, **kwds: self.do('copy-config', *args, **kwds)

    #: :see: :meth:`GetConfig.request() <ncclient.operations.Validate.request>`
    validate = lambda self, *args, **kwds: self.do('validate', *args, **kwds)

    #: :see: :meth:`Commit.request() <ncclient.operations.Commit.request>`
    commit = lambda self, *args, **kwds: self.do('commit', *args, **kwds)

    #: :see: :meth:`DiscardChanges.request() <ncclient.operations.DiscardChanges.request>`
    discard_changes = lambda self, *args, **kwds: self.do('discard-changes', *args, **kwds)

    #: :see: :meth:`DeleteConfig.request() <ncclient.operations.DeleteConfig.request>`
    delete_config = lambda self, *args, **kwds: self.do('delete-config', *args, **kwds)

    #: :see: :meth:`Lock.request() <ncclient.operations.Lock.request>`
    lock = lambda self, *args, **kwds: self.do('lock', *args, **kwds)

    #: :see: :meth:`DiscardChanges.request() <ncclient.operations.Unlock.request>`
    unlock = lambda self, *args, **kwds: self.do('unlock', *args, **kwds)

    #: :see: :meth:`CloseSession.request() <ncclient.operations.CloseSession.request>`
    close_session = lambda self, *args, **kwds: self.do('close-session', *args, **kwds)

    #: :see: :meth:`KillSession.request() <ncclient.operations.KillSession.request>`
    kill_session = lambda self, *args, **kwds: self.do('kill-session', *args, **kwds)

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
            self.close_session()
        except Exception as e:
            logger.debug('error doing <close-session> -- %r' % e)
        if self._session.connected: # if that didn't work...
            self._session.close()

    @property
    def session(self, session):
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
