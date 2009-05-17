*************
Introduction
*************

NCClient is a Python library for NETCONF clients. NETCONF is a network management protocol defined in :rfc:`4741`.

It is meant for Python 2.6+ (not Python 3 yet, though).

The features of NCClient include:

* Request pipelining.
* (A)synchronous RPC requests.
* Keeps XML out of the way unless really needed.
* Supports all operations and capabilities defined in :rfc:`4741`.
* Extensible. New transport mappings and capabilities/operations can be easily added.

The best way to introduce is of course, through a simple code example::

    from ncclient import manager

    with manager.connect_ssh('host', 'username') as m:
        assert(":url" in manager.server_capabilities)
        with m.locked('running'):
            m.copy_config(source="running", target="file://new_checkpoint.conf")
            m.copy_config(source="file://old_checkpoint.conf", target="running")

It is recommended to use the high-level :class:`Manager` API where possible. It exposes almost all of the functionality.

