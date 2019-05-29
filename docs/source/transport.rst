:mod:`~ncclient.transport` -- Transport / Session layer
=======================================================

.. module:: ncclient.transport
    :synopsis: Transport / Session layer

Base types
-----------

.. autoclass:: Session
    :members: add_listener, remove_listener, get_listener_instance, client_capabilities, server_capabilities, connected, id

.. autoclass:: SessionListener
    :members: callback, errback

SSH session implementation
--------------------------

.. automethod:: ssh.default_unknown_host_cb

.. autoclass:: SSHSession
    :show-inheritance:
    :members: load_known_hosts, close, transport

    .. automethod:: connect(host[, port=830, timeout=None, unknown_host_cb=default_unknown_host_cb, username=None, password=None, key_filename=None, allow_agent=True, hostkey_verify=True, hostkey=None, look_for_keys=True, ssh_config=None, bind_addr=None])

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
