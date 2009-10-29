:mod:`~ncclient.manager` -- High-level API
==========================================

.. automodule:: ncclient.manager
    :synopsis: High-level API

Module data
-----------

These attributes control what capabilties are exchanged with the NETCONF server and what operations
are available through the `Manager` API.

.. autodata:: CAPABILITIES

.. autodata:: OPERATIONS

Factory functions
-----------------

A `Manager` instance is created using a factory function.

.. autofunction:: connect_ssh(host[, port=830, timeout=None, unknown_host_cb=default_unknown_host_cb, username=None, password, key_filename=None, allow_agent=True, look_for_keys=True])

.. autodata:: connect

Manager
-------

Exposes an API for RPC operations as method calls. The return type of these methods depends on
whether we are is in :attr:`asynchronous or synchronous mode <ncclient.manager.Manager.async_mode>`.

In synchronous mode replies are awaited and the corresponding `~ncclient.operations.RPCReply` object
is returned. Depending on the :attr:`exception raising mode <ncclient.manager.Manager.raise_mode>`,
an *rpc-error* in the reply may be raised as :exc:`RPCError` exceptions.

However in asynchronous mode, operations return immediately with an `~ncclient.operations.RPC`
object. Error handling and checking for whether a reply has been received must be dealt with
manually. See the `~ncclient.operations.RPC` documentation for details.

Note that in case of the *get* and *get-config* operations, the reply is an instance of
`~ncclient.operations.GetReply` which exposes the additional attributes
:attr:`~ncclient.operations.GetReply.data` (as `~xml.etree.ElementTree.Element`) and
:attr:`~ncclient.operations.GetReply.data_xml` (as `string`), which are of primary interest in case
of these operations.

Presence of capabilities is verified to the extent possible, and you can expect a
:exc:`~ncclient.operations.MissingCapabilityError` if something is amiss. In case of transport-layer
errors, e.g. unexpected session close, :exc:`~ncclient.transport.TransportError` will be raised.

.. class:: Manager
    
    For details on the expected behavior of the operations and their parameters 
    refer to :rfc:`4741`.

    Manager instances are also context managers so you can use it like this::

        with manager.connect("host") as m:
            # do your stuff
    
    ... or like this::
    
        m = manager.connect("host")
        try:
            # do your stuff
        finally:
            m.close()
    
    .. method:: get_config(source[, filter=None])
        
        Retrieve all or part of a specified configuration.
        
        :param source: name of the configuration datastore being queried
        :type source: `string`
        
        :param filter: portions of the device configuration to retrieve (by default entire configuration is retrieved)
        :type filter: :ref:`filter_params`
    
    .. method:: edit_config(target, config[, default_operation=None, test_option=None, error_option=None])
        
        Loads all or part of a specified configuration to the specified target configuration.
        
        The ``"rollback-on-error"`` *error_option* depends on the ``:rollback-on-error`` capability.
        
        :param target: name of the configuration datastore being edited
        :type target: `string`
        
        :param config: configuration (must be rooted in *<config> .. </config>*)
        :type config: `string` or `~xml.etree.ElementTree.Element`
        
        :param default_operation: one of { ``"merge"``, ``"replace"``, or ``"none"`` }
        :type default_operation: `string`
        
        :param test_option: one of { ``"test_then_set"``, ``"set"`` }
        :type test_option: `string`
        
        :param error_option: one of { ``"stop-on-error"``, ``"continue-on-error"``, ``"rollback-on-error"`` }
        :type error_option: `string`
    
    .. method:: copy_config(source, target)
        
        Create or replace an entire configuration datastore with the contents of another complete
        configuration datastore. 
        
        :param source: configuration datastore to use as the source of the copy operation or *<config>* element containing the configuration subtree to copy
        :type source: :ref:`srctarget_params`
        
        :param target: configuration datastore to use as the destination of the copy operation
        :type target: :ref:`srctarget_params`
    
    .. method:: delete_config(target)
        
        Delete a configuration datastore.
        
        :param target: name or URL of configuration datastore to delete
        :type: :ref:`srctarget_params`
    
    .. method:: lock(target)
        
        Allows the client to lock the configuration system of a device.
        
        :param target: name of the configuration datastore to lock
        :type target: `string`
        
    .. method:: unlock(target)
    
        Release a configuration lock, previously obtained with the
        :meth:`~ncclient.manager.Manager.lock` operation.
        
        :param target: name of the configuration datastore to unlock
        :type target: `string`
    
    .. method:: locked(target)
        
        Returns a context manager for a lock on a datastore, e.g.::
        
            with m.locked("running"):
                # do your stuff

        ... instead of::
        
            m.lock("running")
            try:
                # do your stuff
            finally:
                m.unlock("running")
        
        :param target: name of configuration datastore to lock
        :type target: `string`
        
        :rtype: `~ncclient.operations.LockContext`
    
    .. method:: get([filter=None])
        
        Retrieve running configuration and device state information.
        
        :param filter: portions of the device configuration to retrieve (by default entire configuration is retrieved)
        :type filter: :ref:`filter_params`
    
    .. method:: close_session()
        
        Request graceful termination of the NETCONF session, and also close the transport.
    
    .. method:: kill_session(session_id)
        
        Force the termination of a NETCONF session (not the current one!).
        
        :param session_id: session identifier of the NETCONF session to be terminated
        :type session_id: `string`
    
    .. method:: commit([confirmed=False, timeout=None])
    
        Commit the candidate configuration as the device's new current configuration. Depends on the
        *:candidate* capability.
        
        A confirmed commit (i.e. if *confirmed* is :const:`True`) is reverted if there is no
        followup commit within the *timeout* interval. If no timeout is specified the confirm
        timeout defaults to 600 seconds (10 minutes). A confirming commit may have the *confirmed*
        parameter but this is not required. Depends on the *:confirmed-commit* capability.
        
        :param confirmed: whether this is a confirmed commit
        :type confirmed: `bool`
        
        :param timeout: confirm timeout in seconds
        :type timeout: `int`
    
    .. method:: discard_changes()
    
        Revert the candidate configuration to the currently running configuration. Any uncommitted
        changes are discarded.
    
    .. method:: validate(source)
        
        Validate the contents of the specified configuration.
        
        :param source: name of the configuration datastore being validated or *<config>* element containing the configuration subtree to be validated
        :type source: :ref:`srctarget_params`
    
    .. attribute:: async_mode
        
        Specify whether operations are executed asynchronously (:const:`True`)
        or synchronously (:const:`False`) (the default).
    
    .. attribute:: raise_mode
        
        Specify which errors are raised as :exc:`~ncclient.operations.RPCError` exceptions.
        Valid values:
        
        * ``"all"`` -- any kind of *rpc-error* (error or warning)
        * ``"errors"`` -- where the *error-type* element says it is an error
        * ``"none"`` -- neither
        
    .. attribute:: client_capabilities
    
        `~ncclient.capabilities.Capabilities` object representing the client's capabilities.
    
    .. attribute:: server_capabilities
    
        `~ncclient.capabilities.Capabilities` object representing the server's capabilities.
    
    .. attribute:: session_id
    
        *session-id* assigned by the NETCONF server.
    
    .. attribute:: connected
        
        Bolean value indicating whether currently connected to the NETCONF server.


Special kinds of parameters
---------------------------

Some parameters can take on different types to keep the interface simple.

.. _srctarget_params:

Source and target parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Where an method takes a *source* or *target* argument, usually a datastore name or URL is expected.
The latter depends on the ``:url`` capability and on whether the specific URL scheme is supported.
Either must be specified as a `string`. For example, ``"running"``,
``"ftp://user:pass@host/config"``.

If the source may be a *<config>* element, e.g. as allowed for the *validate* RPC, it can also be
specified as an XML string or an `~xml.etree.ElementTree.Element` object.

.. _filter_params:

Filter parameters
^^^^^^^^^^^^^^^^^

Where a method takes a *filter* argument, it can take on the following types:

* A ``tuple`` of *(type, criteria)*.
    
    Here *type* has to be one of ``"xpath"`` or ``"subtree"``.
    
    * For ``"xpath"`` the *criteria* should be a `string` containing the XPath expression.
    * For ``"subtree"`` the *criteria* should be an XML string or an
      `~xml.etree.ElementTree.Element` object containing the criteria.

* A *<filter>* element as an XML string or an `~xml.etree.ElementTree.Element` object.
