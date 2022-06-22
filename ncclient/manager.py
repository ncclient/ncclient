# Copyright 2009 Shikhar Bhushan
# Copyright 2011 Leonidas Poulopoulos
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

"""
This module is a thin layer of abstraction around the library.
It exposes all core functionality.
"""

from ncclient import operations
from ncclient import transport
import socket
import logging
import functools

from ncclient.xml_ import *

logger = logging.getLogger('ncclient.manager')

OPERATIONS = {
    "get": operations.Get,
    "get_config": operations.GetConfig,
    "get_schema": operations.GetSchema,
    "dispatch": operations.Dispatch,
    "edit_config": operations.EditConfig,
    "copy_config": operations.CopyConfig,
    "validate": operations.Validate,
    "commit": operations.Commit,
    "discard_changes": operations.DiscardChanges,
    "cancel_commit": operations.CancelCommit,
    "delete_config": operations.DeleteConfig,
    "lock": operations.Lock,
    "unlock": operations.Unlock,
    "create_subscription": operations.CreateSubscription,
    "close_session": operations.CloseSession,
    "kill_session": operations.KillSession,
    "poweroff_machine": operations.PoweroffMachine,
    "reboot_machine": operations.RebootMachine,
    "rpc": operations.GenericRPC,
}

"""
Dictionary of base method names and corresponding :class:`~ncclient.operations.RPC`
subclasses. It is used to lookup operations, e.g. `get_config` is mapped to
:class:`~ncclient.operations.GetConfig`. It is thus possible to add additional
operations to the :class:`Manager` API.

Note: To add readability to the ncclient, you can create new method under
:class:`Manager`. To keep the initial functionality of the module __getitem__ method
is operational.
"""


def make_device_handler(device_params):
    """
    Create a device handler object that provides device specific parameters and
    functions, which are called in various places throughout our code.

    If no device_params are defined or the "name" in the parameter dict is not
    known then a default handler will be returned.

    """
    if device_params is None:
        device_params = {}

    handler = device_params.get('handler', None)
    if handler:
        return handler(device_params)

    device_name = device_params.get("name", "default")
    # Attempt to import device handler class. All device handlers are
    # in a module called "ncclient.devices.<devicename>" and in a class named
    # "<devicename>DeviceHandler", with the first letter capitalized.
    class_name          = "%sDeviceHandler" % device_name.capitalize()
    devices_module_name = "ncclient.devices.%s" % device_name
    dev_module_obj      = __import__(devices_module_name)
    handler_module_obj  = getattr(getattr(dev_module_obj, "devices"), device_name)
    class_obj           = getattr(handler_module_obj, class_name)
    handler_obj         = class_obj(device_params)
    return handler_obj


def _extract_device_params(kwds):
    device_params = kwds.pop("device_params", None)

    return device_params

def _extract_manager_params(kwds):
    manager_params = kwds.pop("manager_params", {})

    # To maintain backward compatibility
    if 'timeout' not in manager_params and 'timeout' in kwds:
        manager_params['timeout'] = kwds['timeout']
    return manager_params

def _extract_nc_params(kwds):
    nc_params = kwds.pop("nc_params", {})

    return nc_params

def connect_ssh(*args, **kwds):
    """Initialize a :class:`Manager` over the SSH transport.
    For documentation of arguments see :meth:`ncclient.transport.SSHSession.connect`.

    The underlying :class:`ncclient.transport.SSHSession` is created with
    :data:`CAPABILITIES`. All the provided arguments are passed directly to its
    implementation of :meth:`~ncclient.transport.SSHSession.connect`.

    To customize the :class:`Manager`, add a `manager_params` dictionary in connection
    parameters (e.g. `manager_params={'timeout': 60}` for a bigger RPC timeout parameter)

    To invoke advanced vendor related operation add
    `device_params={'name': '<vendor_alias>'}` in connection parameters. For the time,
    'junos' and 'nexus' are supported for Juniper and Cisco Nexus respectively.

    A custom device handler can be provided with
    `device_params={'handler':<handler class>}` in connection parameters.

    """
    # Extract device/manager/netconf parameter dictionaries, if they were passed into this function.
    # Remove them from kwds (which should keep only session.connect() parameters).
    device_params = _extract_device_params(kwds)
    manager_params = _extract_manager_params(kwds)
    nc_params = _extract_nc_params(kwds)

    device_handler = make_device_handler(device_params)
    device_handler.add_additional_ssh_connect_params(kwds)
    device_handler.add_additional_netconf_params(nc_params)
    session = transport.SSHSession(device_handler)

    try:
       session.connect(*args, **kwds)
    except Exception as ex:
        if session.transport:
            session.close()
        raise
    return Manager(session, device_handler, **manager_params)


def connect_ioproc(*args, **kwds):
    device_params = _extract_device_params(kwds)
    manager_params = _extract_manager_params(kwds)

    if device_params:
        import_string = 'ncclient.transport.third_party.'
        import_string += device_params['name'] + '.ioproc'
        third_party_import = __import__(import_string, fromlist=['IOProc'])

    device_handler = make_device_handler(device_params)

    session = third_party_import.IOProc(device_handler)
    session.connect()

    return Manager(session, device_handler, **manager_params)


def connect(*args, **kwds):
    if "host" in kwds:
        host = kwds["host"]
        device_params = kwds.get('device_params', {})
        if host == 'localhost' and device_params.get('name') == 'junos' \
                and device_params.get('local'):
            return connect_ioproc(*args, **kwds)
        else:
            return connect_ssh(*args, **kwds)

def call_home(*args, **kwds):
    host = kwds["host"]
    port = kwds.get("port",4334)
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.bind((host, port))
    srv_socket.settimeout(10)
    srv_socket.listen()

    sock, remote_host = srv_socket.accept()
    logger.info('Callhome connection initiated from remote host {0}'.format(remote_host))
    kwds['sock'] = sock
    return connect_ssh(*args, **kwds)

class Manager(object):

    """
    For details on the expected behavior of the operations and their
        parameters refer to :rfc:`6241`.

    Manager instances are also context managers so you can use it like this::

        with manager.connect("host") as m:
            # do your stuff

    ... or like this::

        m = manager.connect("host")
        try:
            # do your stuff
        finally:
            m.close_session()
    """

   # __metaclass__ = OpExecutor


    HUGE_TREE_DEFAULT = False
    """Default for `huge_tree` support for XML parsing of RPC replies (defaults to False)"""

    def __init__(self, session, device_handler, timeout=30):
        self._session = session
        self._async_mode = False
        self._timeout = timeout
        self._raise_mode = operations.RaiseMode.ALL
        self._huge_tree = self.HUGE_TREE_DEFAULT
        self._device_handler = device_handler
        self._vendor_operations = {}
        if device_handler:
            self._vendor_operations.update(device_handler.add_additional_operations())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close_session()
        return False

    def __set_timeout(self, timeout):
        self._timeout = timeout

    def __set_async_mode(self, mode):
        self._async_mode = mode

    def __set_raise_mode(self, mode):
        assert(mode in (operations.RaiseMode.NONE, operations.RaiseMode.ERRORS, operations.RaiseMode.ALL))
        self._raise_mode = mode

    def execute(self, cls, *args, **kwds):
        return cls(self._session,
                   device_handler=self._device_handler,
                   async_mode=self._async_mode,
                   timeout=self._timeout,
                   raise_mode=self._raise_mode,
                   huge_tree=self._huge_tree).request(*args, **kwds)

    def locked(self, target):
        """Returns a context manager for a lock on a datastore, where
        *target* is the name of the configuration datastore to lock, e.g.::

            with m.locked("running"):
                # do your stuff

        ... instead of::

            m.lock("running")
            try:
                # do your stuff
            finally:
                m.unlock("running")
        """
        return operations.LockContext(self._session, self._device_handler, target)
    
    def get(self, *args, **kwargs):
        """Retrieve running configuration and device state information.

        *filter* specifies the portion of the configuration to retrieve (by default entire configuration is retrieved)

        *with_defaults* defines an explicit method of retrieving default values from the configuration (see :rfc:`6243`)
        """
        return self.execute(operations.Get, *args, **kwargs)
    
    def get_config(self, *args, **kwargs):
        """Retrieve all or part of a specified configuration.

        *source* name of the configuration datastore being queried. e.g. 'running'

        *filter* specifies the portion of the configuration to retrieve (by default entire configuration is retrieved)

        *with_defaults* defines an explicit method of retrieving default values from the configuration (see :rfc:`6243`)
        """
        return self.execute(operations.GetConfig, *args, **kwargs)

    def dispatch(self, *args, **kwargs):
        """
        *rpc_command* specifies rpc command to be dispatched either in plain text or in xml element format (depending on command)

        *source* name of the configuration datastore being queried

        *filter* specifies the portion of the configuration to retrieve (by default entire configuration is retrieved)

        Examples of usage::

            dispatch('clear-arp-table')

        or dispatch element like ::

            xsd_fetch = new_ele('get-xnm-information')
            sub_ele(xsd_fetch, 'type').text="xml-schema"
            sub_ele(xsd_fetch, 'namespace').text="junos-configuration"
            dispatch(xsd_fetch)
        """
        return self.execute(operations.Dispatch, *args, **kwargs)
    
    def get_schema(self, *args, **kwargs):
        """Retrieve a named schema, with optional revision and type.

        *identifier* name of the schema to be retrieved

        *version* version of schema to get

        *format* format of the schema to be retrieved, yang is the default
        """
        return self.execute(operations.GetSchema, *args, **kwargs)
    
    def edit_config(self, *args, **kwargs):
        """Loads all or part of the specified *config* to the *target* configuration datastore.

        *target* is the name of the configuration datastore being edited. e.g. 'running'

        *config* is the configuration, which must be rooted in the `config` element. It can be specified either as a string or an :class:`~xml.etree.ElementTree.Element`.

        *default_operation* if specified must be one of { `"merge"`, `"replace"`, or `"none"` }

        *test_option* if specified must be one of { `"test-then-set"`, `"set"`, `"test-only"` }

        *error_option* if specified must be one of { `"stop-on-error"`, `"continue-on-error"`, `"rollback-on-error"` }

        The `"rollback-on-error"` *error_option* depends on the `:rollback-on-error` capability.
        """
        return self.execute(operations.EditConfig, *args, **kwargs)

    def copy_config(self, *args, **kwargs):
        """Create or replace an entire configuration datastore with the contents of another complete
        configuration datastore.

        *source* is the name of the configuration datastore to use as the source of the copy operation or `config` element containing the configuration subtree to copy

        *target* is the name of the configuration datastore to use as the destination of the copy operation
        """
        return self.execute(operations.CopyConfig, *args, **kwargs)

    def validate(self, *args, **kwargs):
        """Validate the contents of the specified configuration.

        *source* is the name of the configuration datastore being validated or `config` element containing the configuration subtree to be validated
        """
        return self.execute(operations.Validate, *args, **kwargs)

    def commit(self, *args, **kwargs):
        """Commit the candidate configuration as the device's new current configuration. Depends on the `:candidate` capability.

        A confirmed commit (i.e. if *confirmed* is `True`) is reverted if there is no followup commit within the *timeout* interval. If no timeout is specified the confirm timeout defaults to 600 seconds (10 minutes). A confirming commit may have the *confirmed* parameter but this is not required. Depends on the `:confirmed-commit` capability.

        *confirmed* whether this is a confirmed commit

        *timeout* specifies the confirm timeout in seconds

        *persist* make the confirmed commit survive a session termination, and set a token on the ongoing confirmed commit

        *persist_id* value must be equal to the value given in the <persist> parameter to the original <commit> operation.
        """
        return self.execute(operations.Commit, *args, **kwargs)

    def discard_changes(self, *args, **kwargs):
        """Revert the candidate configuration to the currently running configuration. Any uncommitted changes are discarded."""
        return self.execute(operations.DiscardChanges, *args, **kwargs)

    def cancel_commit(self, *args, **kwargs):
        """Cancel an ongoing confirmed commit. Depends on the `:candidate` and `:confirmed-commit` capabilities.

        *persist-id* value must be equal to the value given in the <persist> parameter to the previous <commit> operation.
        """
        return self.execute(operations.CancelCommit, *args, **kwargs)

    def delete_config(self, *args, **kwargs):
        """Delete a configuration datastore.

        *target* specifies the  name or URL of configuration datastore to delete"""
        return self.execute(operations.DeleteConfig, *args, **kwargs)

    def create_subscription(self, *args, **kwargs):
        """Creates a subscription for notifications from the server.

        *filter* specifies the subset of notifications to receive (by
        default all notificaitons are received)

        :seealso: :ref:`filter_params`

        *stream_name* specifies the notification stream name. The
        default is None meaning all streams.

        *start_time* triggers the notification replay feature to
        replay notifications from the given time. The default is None,
        meaning that this is not a replay subscription. The format is
        an RFC 3339/ISO 8601 date and time.

        *stop_time* indicates the end of the notifications of
        interest. This parameter must be used with *start_time*. The
        default is None, meaning that (if *start_time* is present) the
        notifications will continue until the subscription is
        terminated. The format is an RFC 3339/ISO 8601 date and time.

        """
        return self.execute(operations.CreateSubscription, *args, **kwargs)

    def close_session(self, *args, **kwargs):
        "Request graceful termination of the NETCONF session, and also close the transport."
        return self.execute(operations.CloseSession, *args, **kwargs)

    def kill_session(self, *args, **kwargs):
        """Force the termination of a NETCONF session (not the current one!)

        *session_id* is the session identifier of the NETCONF session to be terminated as a string
        """
        return self.execute(operations.KillSession, *args, **kwargs)

    def poweroff_machine(self, *args, **kwargs):
        """Flowmon rfc. Power off the machine"""
        return self.execute(operations.PoweroffMachine, *args, **kwargs)

    def reboot_machine(self, *args, **kwargs):
        """Flowmon rfc. Reboot the machine"""
        return self.execute(operations.RebootMachine, *args, **kwargs)

    def rpc(self, *args, **kwargs):
        """
        *rpc_command* specifies rpc command to be dispatched either in plain text or in xml element format (depending on command)

        *target* name of the configuration datastore being edited

        *source* name of the configuration datastore being queried

        *config* is the configuration, which must be rooted in the `config` element. It can be specified either as a string or an :class:`~xml.etree.ElementTree.Element`.

        *filter* specifies the portion of the configuration to retrieve (by default entire configuration is retrieved)

        :seealso: :ref:`filter_params`

        Examples of usage::

            m.rpc('rpc_command')

        or dispatch element like ::

            rpc_command = new_ele('get-xnm-information')
            sub_ele(rpc_command, 'type').text = "xml-schema"
            m.rpc(rpc_command)
        """
        return self.execute(operations.GenericRPC, *args, **kwargs)

    def scp(self):
        return self._session.scp()

    def session(self):
        raise NotImplementedError

    def __getattr__(self, method):
        if method in self._vendor_operations:
            return functools.partial(self.execute, self._vendor_operations[method])
        elif method in OPERATIONS:
            return functools.partial(self.execute, OPERATIONS[method])
        else:
            """Parse args/kwargs correctly in order to build XML element"""
            def _missing(*args, **kwargs):
                m = method.replace('_', '-')
                root = new_ele(m)
                if args:
                    for arg in args:
                        sub_ele(root, arg)
                r = self.rpc(root)
                return r
            return _missing

    def take_notification(self, block=True, timeout=None):
        """Attempt to retrieve one notification from the queue of received
        notifications.

        If block is True, the call will wait until a notification is
        received.

        If timeout is a number greater than 0, the call will wait that
        many seconds to receive a notification before timing out.

        If there is no notification available when block is False or
        when the timeout has elapse, None will be returned.

        Otherwise a :class:`~ncclient.operations.notify.Notification`
        object will be returned.
        """
        return self._session.take_notification(block, timeout)

    @property
    def client_capabilities(self):
        """:class:`~ncclient.capabilities.Capabilities` object representing
        the client's capabilities."""
        return self._session._client_capabilities

    @property
    def server_capabilities(self):
        """:class:`~ncclient.capabilities.Capabilities` object representing
        the server's capabilities."""
        return self._session._server_capabilities

    @property
    def channel_id(self):
        return self._session._channel_id

    @property
    def channel_name(self):
        return self._session._channel_name

    @property
    def session_id(self):
        """`session-id` assigned by the NETCONF server."""
        return self._session.id

    @property
    def connected(self):
        """Whether currently connected to the NETCONF server."""
        return self._session.connected

    async_mode = property(fget=lambda self: self._async_mode,
                          fset=__set_async_mode)
    """Specify whether operations are executed asynchronously (`True`) or
    synchronously (`False`) (the default)."""

    timeout = property(fget=lambda self: self._timeout, fset=__set_timeout)
    """Specify the timeout for synchronous RPC requests."""

    raise_mode = property(fget=lambda self: self._raise_mode,
                          fset=__set_raise_mode)
    """Specify which errors are raised as :exc:`~ncclient.operations.RPCError`
    exceptions. Valid values are the constants defined in
    :class:`~ncclient.operations.RaiseMode`.
    The default value is :attr:`~ncclient.operations.RaiseMode.ALL`."""

    @property
    def huge_tree(self):
        """Whether `huge_tree` support for XML parsing of RPC replies is enabled (default=False)
        The default value is configurable through :attr:`~ncclient.manager.Manager.HUGE_TREE_DEFAULT`"""
        return self._huge_tree

    @huge_tree.setter
    def huge_tree(self, x):
        self._huge_tree = x
