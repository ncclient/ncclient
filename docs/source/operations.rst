:mod:`~ncclient.operations` -- Everything RPC
=============================================


.. module:: ncclient.operations
    :synopsis: Everything RPC

.. autoclass:: RaiseMode
    :members: NONE, ERRORS, ALL

Base classes
------------

.. autoclass:: RPC(session, async=False, timeout=None, raise_mode="none")
    :members: DEPENDS, REPLY_CLS, _assert, _request, request, event, error, reply, raise_mode, is_async, timeout

.. autoclass:: RPCReply
    :members: xml, ok, error, errors, _parsing_hook

.. autoexception:: RPCError
    :show-inheritance:
    :members: type, severity, tag, path, message, info

Operations
----------

The operation classes are currently undocumented. See documentation of :class:`~ncclient.manager.Manager` for methods that utilize the operation classes. The parameters accepted by :meth:`~RPC.request` for these classes are the same.

Replies with data
-----------------

.. autoclass:: GetReply
    :show-inheritance:
    :members: data, data_ele, data_xml

Exceptions
----------

.. autoexception:: OperationError
    :show-inheritance:

.. autoexception:: MissingCapabilityError
    :show-inheritance:

.. autoexception:: TimeoutExpiredError
    :show-inheritance: