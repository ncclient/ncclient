*********************
:mod:`manager` module
*********************

.. module:: ncclient.manager

Dealing with RPC errors
=======================

These constants define what :class:`Manager` does when an *<rpc-error>* element is encountered in a reply.

.. autodata:: RAISE_ALL

.. autodata:: RAISE_ERR

.. autodata:: RAISE_NONE


Manager instances
=================

:class:`Manager` instances are created by the :meth:`connect` family of factory functions. Currently only :meth:`connect_ssh` is available.

.. autofunction:: connect

.. autofunction:: connect_ssh


.. autoclass:: Manager
    :members: set_rpc_error_action, get, get_config, edit_config, copy_config, validate, commit, discard_changes, delete_config, lock, unlock, close_session, kill_session, locked, close, client_capabilities, server_capabilities, session_id, connected
