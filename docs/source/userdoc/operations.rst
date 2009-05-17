************************
:mod:`operations` module
************************

.. automodule:: ncclient.operations
    :synopsis: RPC and Operation layers

Base types
==========

.. currentmodule:: ncclient.operations.rpc

.. autoclass:: RPC(session[, async=False, timeout=None])
    :members: set_async, set_timeout, reply, error, event, async, timeout, id, session

.. autoclass:: RPCReply
    :members: ok, error, errors

.. autoclass:: RPCError
    :members: type, severity, tag, path, message, info
    :show-inheritance:

NETCONF Operations
==================

.. currentmodule:: ncclient.operations

Dependencies
-------------

Operations may have a hard dependency on some capability, or the dependency may arise at request-time due to an optional argument. In any case, a :exc:`MissingCapabilityError` is raised if the server does not support the relevant capability.

.. _return:

Return type
-----------

The return type for the :meth:`request` method depends of an operation on whether it is synchronous or asynchronous (see base class :class:`RPC`).

* For synchronous requests, it will block waiting for the reply, and once it has been received an :class:`RPCReply` object is returned. If an error occured while waiting for the reply, it will be raised.

* For asynchronous requests, it will immediately return an :class:`~threading.Event` object. This event is set when a reply is received, or an error occurs that prevents a reply from being received. The :attr:`~RPC.reply` and :attr:`~RPC.error` attributes can then be accessed to determine which of the two it was :-)

General notes on parameters
----------------------------

.. _source_target:

Source / target parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Where an operation takes a source or target parameter, it is mainly the case that it can be a datastore name or a URL. The latter, of course, depends on the *:url* capability and whether the capability supports the specific schema of the URL. Either must be specified as a `string`.

If the source may be a *<config>* element, e.g. for :class:`Validate`, specify in :ref:`dtree` with the root element as *<config>*.

.. _filter:

Filter parameters
^^^^^^^^^^^^^^^^^^

Filter parameters, where applicable, can take one of the following types:

* A `tuple` of *(type, criteria)*.
    Here type has to be one of "xpath" or "subtree". For type "xpath", the criteria should be a `string` that is a valid XPath expression. For type "subtree", criteria should be in :ref:`dtree` representing a valid subtree filter.
* A valid *<filter>* element in :ref:`dtree`.

Retrieval operations
--------------------

The reply object for these operations will be a :class:`GetReply` instance.

.. autoclass:: Get
    :show-inheritance:
    :members: request

.. autoclass:: GetConfig
    :show-inheritance:
    :members: request

.. autoclass:: GetReply
    :show-inheritance:
    :members: data, data_xml, data_dtree, data_ele

Locking operations
------------------

.. autoclass:: Lock
    :show-inheritance:
    :members: request

.. autoclass:: Unlock
    :show-inheritance:
    :members: request

Configuration operations
-------------------------

.. autoclass:: EditConfig
    :show-inheritance:
    :members: request

.. autoclass:: CopyConfig
    :show-inheritance:
    :members: request

.. autoclass:: DeleteConfig
    :show-inheritance:
    :members: request

.. autoclass:: Validate
    :show-inheritance:
    :members: request

.. autoclass:: Commit
    :show-inheritance:
    :members: request

.. autoclass:: DiscardChanges
    :show-inheritance:
    :members: request

Session management operations
------------------------------

.. autoclass:: CloseSession
    :show-inheritance:
    :members: request

.. autoclass:: KillSession
    :show-inheritance:
    :members: request

Also useful
-----------

.. autoclass:: LockContext


Errors
=======

.. autoexception:: OperationError
    :show-inheritance:
    :members:

.. autoexception:: TimeoutExpiredError
    :show-inheritance:
    :members:

.. autoexception:: MissingCapabilityError
    :show-inheritance:
    :members: