import logging
import functools
from ncclient import operations
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
}

"""
Dictionary of base method names and corresponding :class:`~ncclient.operations.RPC`
subclasses. It is used to lookup operations, e.g. `get_config` is mapped to
:class:`~ncclient.operations.GetConfig`. It is thus possible to add additional
operations to the :class:`Manager` API.
"""

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

    def rpc(self, *args, **kwds):
        return operations.GenericRPC(self._session,
                                     self._device_handler,
                                     async_mode=self._async_mode,
                                     timeout=self._timeout,
                                     raise_mode=self._raise_mode,
                                     huge_tree=self._huge_tree).request(*args, **kwds)

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

    @property
    def session(self):
        "The `~ncclient.transport.Session` object associated with this RPC."
        return self._session

    @property
    def device_handler(self):
        return self._device_handler

