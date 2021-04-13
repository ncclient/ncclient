:mod:`~ncclient.manager` -- High-level API
==========================================

.. automodule:: ncclient.manager
    :synopsis: High-level API


Customizing
------------

These attributes control what capabilties are exchanged with the NETCONF server and what operations are available through the :class:`Manager` API.

.. autodata:: OPERATIONS



Factory functions
-----------------

A :class:`Manager` instance is created using a factory function.

.. autofunction:: connect_ssh

.. autodata:: connect

Manager
-------

Exposes an API for RPC operations as method calls. The return type of these methods depends on whether we are in :attr:`asynchronous or synchronous mode <ncclient.manager.Manager.async_mode>`.

In synchronous mode replies are awaited and the corresponding :class:`~ncclient.operations.RPCReply` object is returned. Depending on the :attr:`exception raising mode <ncclient.manager.Manager.raise_mode>`, an `rpc-error` in the reply may be raised as an :exc:`~ncclient.operations.RPCError` exception.

However in asynchronous mode, operations return immediately with the corresponding :class:`~ncclient.operations.RPC` object. Error handling and checking for whether a reply has been received must be dealt with manually. See the :class:`~ncclient.operations.RPC` documentation for details.

Note that in case of the :meth:`~Manager.get` and :meth:`~Manager.get_config` operations, the reply is an instance of :class:`~ncclient.operations.GetReply` which exposes the additional attributes :attr:`~ncclient.operations.GetReply.data` (as :class:`~lxml.etree._Element`) and :attr:`~ncclient.operations.GetReply.data_xml` (as a string), which are of primary interest in case of these operations.

Presence of capabilities is verified to the extent possible, and you can expect a :exc:`~ncclient.operations.MissingCapabilityError` if something is amiss. In case of transport-layer errors, e.g. unexpected session close, :exc:`~ncclient.transport.TransportError` will be raised.

.. autoclass:: Manager

    .. autoattribute:: HUGE_TREE_DEFAULT

    .. method:: get_config(source, filter=None, with_defaults=None)

       `get_config` is mapped to :class:`~ncclient.operations.GetConfig`

    .. method:: get_schema(identifier, version=None, format=None)

       `get_schema` is mapped to :class:`~ncclient.operations.GetSchema`

    .. method:: edit_config(config, format='xml', target='candidate', default_operation=None, test_option=None, error_option=None)

       `edit_config` is mapped to :class:`~ncclient.operations.EditConfig`

    .. method:: copy_config(source, target)

       `copy_config` is mapped to :class:`~ncclient.operations.CopyConfig`

    .. method:: delete_config(target)

       `delete_config` is mapped to :class:`~ncclient.operations.DeleteConfig`

    .. method:: dispatch(rpc_command, source=None, filter=None)

       `dispatch` is mapped to :class:`~ncclient.operations.Dispatch`

    .. method:: lock(target="candidate")

       `lock` is mapped to :class:`~ncclient.operations.Lock`

    .. method:: unlock(target="candidate")

       `unlock` is mapped to :class:`~ncclient.operations.Unlock`

    .. method:: get(filter=None, with_defaults=None)

       `get` is mapped to :class:`~ncclient.operations.Get`

    .. method:: close_session()

       `close_session` is mapped to :class:`~ncclient.operations.CloseSession`

    .. method:: kill_session(session_id)

       `kill_session` is mapped to :class:`~ncclient.operations.KillSession`

    .. method:: commit(confirmed=False, timeout=None, persist=None, persist_id=None)

       `commit` is mapped to :class:`~ncclient.operations.Commit`

    .. method:: cancel_commit(persist_id=None)

       `cancel_commit` is mapped to :class:`~ncclient.operations.CancelCommit`

    .. method:: discard_changes()

       `discard_changes` is mapped to :class:`~ncclient.operations.DiscardChanges`

    .. method:: validate(source="candidate")

       `validate` is mapped to :class:`~ncclient.operations.Validate`

    .. method:: create_subscription(filter=None, stream_name=None, start_time=None, stop_time=None)

       `create_subscription` is mapped to :class:`~ncclient.operations.CreateSubscription`

    .. method:: reboot_machine()

       `reboot_machine` is mapped to :class:`~ncclient.operations.RebootMachine`

    .. method:: poweroff_machine()

       `poweroff_machine` is mapped to :class:`~ncclient.operations.PoweroffMachine`

    .. automethod:: locked(target)

    .. automethod:: take_notification(block=True, timeout=None)

    .. autoattribute:: async_mode

    .. autoattribute:: timeout

    .. autoattribute:: raise_mode

    .. autoattribute:: client_capabilities

    .. autoattribute:: server_capabilities

    .. autoattribute:: session_id

    .. autoattribute:: connected

    .. autoattribute:: huge_tree

Special kinds of parameters
---------------------------

Some parameters can take on different types to keep the interface simple.

.. _srctarget_params:

Source and target parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Where an method takes a *source* or *target* argument, usually a datastore name or URL is expected. The latter depends on the `:url` capability and on whether the specific URL scheme is supported. Either must be specified as a string. For example, `"running"`, `"ftp://user:pass@host/config"`.

If the source may be a `config` element, e.g. as allowed for the `validate` RPC, it can also be specified as an XML string or an :class:`~xml.etree.ElementTree.Element` object.

.. _filter_params:

Filter parameters
^^^^^^^^^^^^^^^^^

Where a method takes a *filter* argument, it can take on the following types:

* A tuple of *(type, criteria)*.

    Here *type* has to be one of `"xpath"` or `"subtree"`.

    * For `"xpath"` the *criteria* should be a string containing the XPath expression or a tuple containing a dict of namespace mapping and the XPath expression.
    * For `"subtree"` the *criteria* should be an XML string or an :class:`~xml.etree.ElementTree.Element` object containing the criteria.

* A list of *spec*

    Here *type* has to be `"subtree"`.

    * the *spec* should be a list containing multiple XML string or multiple :class:`~xml.etree.ElementTree.Element` objects.

* A `<filter>` element as an XML string or an :class:`~xml.etree.ElementTree.Element` object.
