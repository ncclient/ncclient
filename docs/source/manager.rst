:mod:`~ncclient.manager` -- High-level API
==========================================

.. module:: ncclient.manager
    :synopsis: High-level API

Factory functions
-----------------

A `Manager` instance is created using a factory function.

.. function:: connect_ssh(host[, port=830, timeout=None, unknown_host_cb=default_unknown_host_cb, username=None, password, key_filename=None, allow_agent=True, look_for_keys=True])
    
    Initializes a NETCONF session over SSH, and creates a connected `Manager`
    instance. *host* must be specified, all the other arguments are optional and
    depend on the kind of host key verification and user authentication you want
    to complete.
    
    For the purpose of host key verification, on POSIX systems a user's
    :file:`~/.ssh/known_hosts` file is automatically considered. The
    *unknown_host_cb* argument specifies a callback that will be invoked when
    the server's host key cannot be verified. See
    :func:`~ncclient.transport.ssh.default_known_host_cb` for function signature.
    
    First, ``publickey`` authentication is attempted. If a specific
    *key_filename* is specified, it will be loaded and authentication attempted
    using it. If *allow_agent* is :const:`True` and an SSH agent is running, the keys
    provided by the agent will be tried. If *look_for_keys* is :const:`True`, keys in
    the :file:`~/.ssh/id_rsa` and :file:`~.ssh/id_dsa` will be tried. In case an
    encrypted key file is encountered, the *password* argument will be used as a
    decryption passphrase.
    
    If ``publickey`` authentication fails and the *password* argument has been
    supplied, ``password`` / ``keyboard-interactive`` SSH authentication will be
    attempted.
    
    :param host: hostname or address on which to connect
    :type host: `string`
    
    :param port: port on which to connect
    :type port: `int`
    
    :param timeout: timeout for socket connect
    :type timeout: `int`
    
    :param unknown_host_cb: optional; callback that is invoked when host key
                            verification fails
    :type unknown_host_cb: `function`
    
    :param username: username to authenticate with, if not specified the
                        username of the logged-in user is used
    :type username: `string`
    
    :param password: password for ``password`` authentication or passphrase for
                        decrypting private key files
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
    
.. function:: connect()

    Same as :func:`connect_ssh`, since SSH is the default (and currently, the
    only) transport.

Manager
-------

Exposes an API for RPC operations as method calls. The return type of these
methods depends on whether we are is in :attr:`asynchronous or synchronous
mode <ncclient.manager.Manager.async_mode>`.

In synchronous mode replies are awaited and the corresponding
`~ncclient.operations.RPCReply` object is returned. Depending on the
:attr:`exception raising mode <ncclient.manager.Manager.raise_mode>`, an
*rpc-error* in the reply may be raised as :exc:`RPCError` exceptions.

However in asynchronous mode, operations return immediately with an
`~ncclient.operations.RPC` object. Error handling and checking for whether a
reply has been received must be dealt with manually. See the
`~ncclient.operations.RPC` documentation for details.

Note that in case of the *get* and *get-config* operations, the reply is an
instance of `~ncclient.operations.GetReply` which exposes the additional
attributes :attr:`~ncclient.operations.GetReply.data`
(as `~xml.etree.ElementTree.Element`) and
:attr:`~ncclient.operations.GetReply.data_xml` (as `string`), which are of primary
interest in case of these operations.

Presence of capabilities is verified to the extent possible, and you can expect
a :exc:`~ncclient.operations.MissingCapabilityError` if something is amiss. In
case of transport-layer errors, e.g. unexpected session close,
:exc:`~ncclient.transport.TransportError` will be raised.

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
        
        :param filter: see :ref:`filter_params`
    
    .. method:: edit_config(target, config[, default_operation=None, test_option=None, error_option=None])
        
        Loads all or part of a specified configuration to the specified target configuration.
        
        The ``"rollback-on-error"`` *error_option* depends on the ``:rollback-on-error`` capability.
        
        :param target: name of the configuration datastore being edited
        :type target: `string`
        
        :param default_operation: one of { ``"merge"``, ``"replace"``, or ``"none"`` }
        :type default_operation: `string`
        
        :param test_option: one of { ``"test_then_set"``, ``"set"`` }
        :type test_option: `string`
        
        :param error_option: one of { ``"stop-on-error"``, ``"continue-on-error"``, ``"rollback-on-error"`` }
        :type error_option: `string`
        
        :param config: *<config>* element as an XML string or `~xml.etree.ElementTree.Element` object
    
    .. method:: copy_config(source, target)
        
        Create or replace an entire configuration datastore with the contents of
        another complete configuration datastore. 
        
        :param source: see :ref:`srctarget_params`
        
        :param target: see :ref:`srctarget_params`
    
    .. method:: delete_config(target)
        
        Delete a configuration datastore.
        
        :param target: see :ref:`srctarget_params`
    
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
        
        :param target: datastore name. See :ref:`srctarget_params`
        
        :rtype: `~ncclient.operations.LockContext`
    
    .. method:: get([filter=None])
        
        Retrieve running configuration and device state information.
        
        :param filter: see :ref:`filter_params`
    
    .. method:: close_session()
        
        Request graceful termination of the NETCONF session, and also close the
        transport.
    
    .. method:: kill_session(session_id)
        
        Force the termination of a NETCONF session (not the current one!).
        
        :param session_id: session identifier of the NETCONF session to be
                            terminated
        :type session_id: `string`
    
    .. attribute:: async_mode
        
        Specify whether operations are executed asynchronously (:const:`True`)
        or synchronously (:const:`False`) (the default).
    
    .. attribute:: raise_mode
        
        The raise *mode* affects what errors are raised as
        :exc:`~ncclient.operations.RPCError` exceptions.
        
        * ``"all"`` -- any kind of *rpc-error* (error or warning)
        * ``"errors"`` -- where the *error-type* attribute says it is an error
        * ``"none"`` -- neither
        
    .. attribute:: client_capabilities
    
        `~ncclient.capabilities.Capabilities` object representing the client's
        capabilities.
    
    .. attribute:: server_capabilities
    
        `~ncclient.capabilities.Capabilities` object representing the server's
        capabilities.
    
    .. attribute:: session_id
    
        The *session-id* assigned by the NETCONF server.
    
    .. attribute:: connected
        
        A boolean value indicating whether currently connected to the NETCONF
        server.


Special kinds of parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To keep the API clean, some parameters can take on different types.

.. _srctarget_params:

Source and target parameters
""""""""""""""""""""""""""""

Where an method takes a *source* or *target* argument, usually a datastore name
or URL is expected. The latter depends on the ``:url`` capability and on whether
the specific URL scheme is supported. Either must be specified as a `string`.
For example, ``"running"``, ``"ftp://user:pass@host/config"``.

If the source may be a *<config>* element, e.g. as allowed for the *validate*
RPC, it can be specified either as an XML string or an
`~xml.etree.ElementTree.Element` object rooted in the *<config>* element.

.. _filter_params:

Filter parameters
"""""""""""""""""

Where a method takes a *filter* argument, it can take on the following types:

* A ``tuple`` of *(type, criteria)*.
    
    Here *type* has to be one of ``"xpath"`` or ``"subtree"``.
    
    * For ``"xpath"`` the *criteria* should be a `string` containing the XPath
      expression.
    * For ``"subtree"`` the *criteria* should be an XML string or an
      `~xml.etree.ElementTree.Element` object containing the criteria.

* A *<filter>* element as an XML string or an `~xml.etree.ElementTree.Element`
  object.
