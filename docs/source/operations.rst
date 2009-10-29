:mod:`~ncclient.operations` -- Everything RPC
=============================================

Base classes
------------

.. module:: ncclient.operations
    :synopsis: Everything RPC

.. autoclass:: RPC(session[, async=False, timeout=None, raise_mode="none"])
    :members: DEPENDS, REPLY_CLS, _assert, _request, request, event, error, reply, raise_mode, is_async, timeout

.. autoclass:: RPCReply
    :members: xml, ok, error, errors

.. autoexception:: RPCError
    :show-inheritance:
    :members: type, severity, tag, path, message, info

Operations
----------

*TODO* The operation classes are currently undocumented. See documentation of
`~ncclient.manager.Manager` for methods that utilize the operation classes. The parameters accepted
by :meth:`~RPC.request` for these classes are the same.

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