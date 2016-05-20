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

from ncclient import capabilities
from ncclient import operations
from ncclient import transport
import six
import logging

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
    "delete_config": operations.DeleteConfig,
    "lock": operations.Lock,
    "unlock": operations.Unlock,
    "close_session": operations.CloseSession,
    "kill_session": operations.KillSession,
    "poweroff_machine": operations.PoweroffMachine,
    "reboot_machine": operations.RebootMachine,
}

"""
Dictionary of base method names and corresponding :class:`~ncclient.operations.RPC`
subclasses. It is used to lookup operations, e.g. `get_config` is mapped to
:class:`~ncclient.operations.GetConfig`. It is thus possible to add additional
operations to the :class:`Manager` API.
"""

VENDOR_OPERATIONS = {}


def make_device_handler(device_params):
    """
    Create a device handler object that provides device specific parameters and
    functions, which are called in various places throughout our code.

    If no device_params are defined or the "name" in the parameter dict is not
    known then a default handler will be returned.

    """
    if device_params is None:
        device_params = {}

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


def connect_ssh(*args, **kwds):
    """
    Initialize a :class:`Manager` over the SSH transport.
    For documentation of arguments see :meth:`ncclient.transport.SSHSession.connect`.

    The underlying :class:`ncclient.transport.SSHSession` is created with
        :data:`CAPABILITIES`. It is first instructed to
        :meth:`~ncclient.transport.SSHSession.load_known_hosts` and then
        all the provided arguments are passed directly to its implementation
        of :meth:`~ncclient.transport.SSHSession.connect`.

    To invoke advanced vendor related operation add device_params =
        {'name':'<vendor_alias>'} in connection paramerers. For the time,
        'junos' and 'nexus' are supported for Juniper and Cisco Nexus respectively.
    """
    # Extract device parameter dict, if it was passed into this function. Need to
    # remove it from kwds, since the session.connect() doesn't like extra stuff in
    # there.
    if "device_params" in kwds:
        device_params = kwds["device_params"]
        del kwds["device_params"]
    else:
        device_params = None

    device_handler = make_device_handler(device_params)
    device_handler.add_additional_ssh_connect_params(kwds)
    global VENDOR_OPERATIONS
    VENDOR_OPERATIONS.update(device_handler.add_additional_operations())
    session = transport.SSHSession(device_handler)
    if "hostkey_verify" not in kwds or kwds["hostkey_verify"]:
        session.load_known_hosts()

    try:
       session.connect(*args, **kwds)
    except Exception as ex:
        if session.transport:
            session.close()
        raise
    return Manager(session, device_handler, **kwds)

def connect_ioproc(*args, **kwds):
    if "device_params" in kwds:
        device_params = kwds["device_params"]
        del kwds["device_params"]
        import_string = 'ncclient.transport.third_party.'
        import_string += device_params['name'] + '.ioproc'
        third_party_import = __import__(import_string, fromlist=['IOProc'])
    else:
        device_params = None

    device_handler = make_device_handler(device_params)

    global VENDOR_OPERATIONS
    VENDOR_OPERATIONS.update(device_handler.add_additional_operations())
    session = third_party_import.IOProc(device_handler)
    session.connect()

    return Manager(session, device_handler, **kwds)


def connect(*args, **kwds):
    if "host" in kwds:
        host = kwds["host"]
        device_params = kwds.get('device_params', {})
        if host == 'localhost' and device_params.get('name') == 'junos' \
                and device_params.get('local'):
            return connect_ioproc(*args, **kwds)
        else:
            return connect_ssh(*args, **kwds)


class OpExecutor(type):

    def __new__(cls, name, bases, attrs):
        def make_wrapper(op_cls):
            def wrapper(self, *args, **kwds):
                return self.execute(op_cls, *args, **kwds)
            wrapper.__doc__ = op_cls.request.__doc__
            return wrapper
        for op_name, op_cls in six.iteritems(OPERATIONS):
            attrs[op_name] = make_wrapper(op_cls)
        return super(OpExecutor, cls).__new__(cls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        def make_wrapper(op_cls):
            def wrapper(self, *args, **kwds):
                return self.execute(op_cls, *args, **kwds)
            wrapper.__doc__ = op_cls.request.__doc__
            return wrapper
        if VENDOR_OPERATIONS:
            for op_name, op_cls in six.iteritems(VENDOR_OPERATIONS):
                setattr(cls, op_name, make_wrapper(op_cls))
        return super(OpExecutor, cls).__call__(*args, **kwargs)


class Manager(six.with_metaclass(OpExecutor, object)):

    """
    For details on the expected behavior of the operations and their
        parameters refer to :rfc:`4741`.

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

    def __init__(self, session, device_handler, timeout=30, *args, **kwargs):
        self._session = session
        self._async_mode = False
        self._timeout = timeout
        self._raise_mode = operations.RaiseMode.ALL
        self._device_handler = device_handler

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
                   async=self._async_mode,
                   timeout=self._timeout,
                   raise_mode=self._raise_mode).request(*args, **kwds)

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

    def scp(self):
        return self._session.scp()

    def session(self):
        raise NotImplementedError

    def __getattr__(self, method):
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
