:mod:`transport` module 
========================

.. module:: ncclient.transport
    :synopsis: Transport protocol layer
.. moduleauthor:: Shikhar Bhushan <shikhar@schmizz.net>

Base types
-----------

.. autoclass:: Session
    :members: add_listener, remove_listener, get_listener_instance, client_capabilities, server_capabilities, connected, id, can_pipeline

.. autoclass:: SessionListener
    :members: callback, errback

SSH session implementation
--------------------------

.. automethod:: ssh.default_unknown_host_cb

.. autoclass:: SSHSession
    :show-inheritance:
    :members: load_known_hosts, close, transport

    .. automethod:: connect(host[, port=830, timeout=None, username=None, password=None, key_filename=None, allow_agent=True, look_for_keys=True])

Errors
------

.. autoexception:: TransportError
    :show-inheritance:

.. autoexception:: SessionCloseError
    :show-inheritance:

.. autoexception:: SSHError
    :show-inheritance:

.. autoexception:: AuthenticationError
    :show-inheritance:

.. autoexception:: SSHUnknownHostError
    :show-inheritance:

