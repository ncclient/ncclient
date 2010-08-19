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

"This module is a thin layer of abstraction around the library. It exposes all core functionality."

import capabilities
import operations
import transport

import logging

logger = logging.getLogger('ncclient.manager')

CAPABILITIES = [
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
]
"A list of URI's representing the client's capabilities. This is used during the initial capability exchange. Modify this if you need to announce some capability not already included."

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
"""Dictionary of method names and corresponding `~ncclient.operations.RPC` subclasses. It is used to lookup operations, e.g. "get_config" is mapped to `~ncclient.operations.GetConfig`. It is thus possible to add additional operations to the `Manager` API."""

def connect_ssh(*args, **kwds):
    """Initializes a NETCONF session over SSH, and creates a connected `Manager` instance. *host* must be specified, all the other arguments are optional and depend on the kind of host key verification and user authentication you want to complete.
        
    For the purpose of host key verification, on -NIX systems a user's :file:`~/.ssh/known_hosts` file is automatically considered. The *unknown_host_cb* argument specifies a callback that will be invoked when the server's host key cannot be verified. See :func:`~ncclient.transport.ssh.default_unknown_host_cb` for function signature.
    
    First, ``publickey`` authentication is attempted. If a specific *key_filename* is specified, it
    will be loaded and authentication attempted using it. If *allow_agent* is :const:`True` and an
    SSH agent is running, the keys provided by the agent will be tried. If *look_for_keys* is
    :const:`True`, keys in the :file:`~/.ssh/id_rsa` and :file:`~.ssh/id_dsa` will be tried. In case
    an encrypted key file is encountered, the *password* argument will be used as a decryption
    passphrase.
    
    If ``publickey`` authentication fails and the *password* argument has been supplied, ``password`` / ``keyboard-interactive`` SSH authentication will be attempted.
    
    :param host: hostname or address on which to connect
    :type host: `string`
    
    :param port: port on which to connect
    :type port: `int`
    
    :param timeout: timeout for socket connect
    :type timeout: `int`
    
    :param unknown_host_cb: optional; callback that is invoked when host key verification fails
    :type unknown_host_cb: `function`
    
    :param username: username to authenticate with, if not specified the username of the logged-in user is used
    :type username: `string`
    
    :param password: password for ``password`` authentication or passphrase for decrypting private key files
    :type password: `string`
    
    :param key_filename: location of a private key file on the file system
    :type key_filename: `string`
    
    :param allow_agent: whether to try connecting to SSH agent for keys
    :type allow_agent: `bool`
    
    :param look_for_keys: whether to look in usual locations for keys
    :type look_for_keys: `bool`
    
    :raises: :exc:`~ncclient.transport.SSHUnknownHostError`
    :raises: :exc:`~ncclient.transport.AuthenticationError`
    
    :rtype: `Manager`
    """
    session = transport.SSHSession(capabilities.Capabilities(CAPABILITIES))
    session.load_known_hosts()
    session.connect(*args, **kwds)
    return Manager(session)

connect = connect_ssh
"Same as :func:`connect_ssh`, since SSH is the default (and currently, the only) transport."

class OpExecutor(type):
    def __new__(cls, name, bases, attrs):
        def make_wrapper(op_cls):
            def wrapper(self, *args, **kwds):
                return self.execute(op_cls, *args, **kwds)
            wrapper.func_doc = op_cls.request.func_doc
            return wrapper
        for op_name, op_cls in OPERATIONS.iteritems():
            attrs[op_name] = make_wrapper(op_cls)
        return super(OpExecutor, cls).__new__(cls, name, bases, attrs)

class Manager(object):

    __metaclass__ = OpExecutor

    RAISE_NONE = 0
    RAISE_ERRORS = 1
    RAISE_ALL = 2

    def __init__(self, session):
        self._session = session
        self._async_mode = False
        self._timeout = None
        self._raise_mode = self.RAISE_ALL

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close_session()
        return False

    def execute(self, cls, *args, **kwds):
        return cls(self._session,
                   async=self._async_mode,
                   timeout=self._timeout,
                   raise_mode=self._raise_mode).request(*args, **kwds)

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
        assert(choice in (self.RAISE_NONE, self.RAISE_ERRORS, self.RAISE_ALL))
        self._raise_mode = mode

    async_mode = property(fget=lambda self: self._async_mode, fset=set_async_mode)

    raise_mode = property(fget=lambda self: self._raise_mode, fset=set_raise_mode)
