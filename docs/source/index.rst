ncclient documentation
======================

ncclient is a Python library for NETCONF clients. NETCONF is a network management protocol defined in :rfc:`4741`. It is suitable for Python 2.6+ (not Python 3 yet, though), and depends on paramiko, an SSH library.

The objective is to offer an intuitive API that sensibly maps the XML-encoded parameters of NETCONF to Python constructs and idioms. The other features are:

* Supports all operations and capabilities defined in :rfc:`4741`.
* Request pipelining.
* Asynchronous RPC requests.
* Keeping XML out of the way unless really needed.
* Extensible. New transport mappings and capabilities/operations can be easily added.

The best way to introduce is of course, through a simple code example::

    from ncclient import manager

    # use ssh-agent or ~/.ssh keys for auth, and relying on known_hosts
    with manager.connect_ssh("host", username="username") as m:
        assert(":url" in manager.server_capabilities)
        with m.locked("running"):
            m.copy_config(source="running", target="file:///new_checkpoint.conf")
            m.copy_config(source="file:///old_checkpoint.conf", target="running")

Contents:

.. toctree::
    
    manager
    extending

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
