:mod:`~ncclient.operations` -- Everything RPC
=============================================

.. module:: ncclient.operations
    :synopsis: Everything RPC

.. autoclass:: RaiseMode
    :members: NONE, ERRORS, ALL

Base classes
------------

.. autoclass:: RPC
    :members: DEPENDS, REPLY_CLS, _assert, _request, request, event, error, reply, raise_mode, is_async, timeout

.. autoclass:: RPCReply
    :members: xml, ok, error, errors, _parsing_hook

.. autoexception:: RPCError
    :show-inheritance:
    :members: type, severity, tag, path, message, info

Operations
----------

Retrieval
..........

.. autoclass:: Get
    :members: request
    :show-inheritance:

    .. autoattribute:: REPLY_CLS

.. autoclass:: GetConfig
    :members: request
    :show-inheritance:

    .. autoattribute:: REPLY_CLS

.. autoclass:: GetReply
    :show-inheritance:
    :members: data, data_ele, data_xml

.. autoclass:: Dispatch
    :members: request
    :show-inheritance:

    .. autoattribute:: REPLY_CLS

Editing
........

.. autoclass:: EditConfig
    :members: request
    :show-inheritance:

.. autoclass:: DeleteConfig
    :members: request
    :show-inheritance:

.. autoclass:: CopyConfig
    :members: request
    :show-inheritance:

.. autoclass:: Validate
    :members: request
    :show-inheritance:

.. autoclass:: Commit
    :members: request
    :show-inheritance:

.. autoclass:: DiscardChanges
    :members: request
    :show-inheritance:

Locking
........

.. autoclass:: Lock
    :members: request
    :show-inheritance:

.. autoclass:: Unlock
    :members: request
    :show-inheritance:

Session
........

.. autoclass:: CloseSession
    :members: request
    :show-inheritance:

.. autoclass:: KillSession
    :members: request
    :show-inheritance:

Exceptions
----------

.. autoexception:: OperationError
    :show-inheritance:

.. autoexception:: MissingCapabilityError
    :show-inheritance:

.. autoexception:: TimeoutExpiredError
    :show-inheritance:

