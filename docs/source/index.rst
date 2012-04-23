Welcome
=======

`ncclient` is a Python library for NETCONF clients. It aims to offer an intuitive API that sensibly maps the XML-encoded nature of NETCONF to Python constructs and idioms, and make writing network-management scripts easier. Other key features are:

* Supports all operations and capabilities defined in :rfc:`4741`.
* Request pipelining.
* Asynchronous RPC requests.
* Keeping XML out of the way unless really needed.
* Extensible. New transport mappings and capabilities/operations can be easily added.

It is suitable for Python 2.6+ (not Python 3 yet, though), and depends on `paramiko 1.7.7.1+ <http://www.lag.net/paramiko/>`_, an SSH library.

The best way to introduce is through a simple code example::

    from ncclient import manager

    # use unencrypted keys from ssh-agent or ~/.ssh keys, and rely on known_hosts
    with manager.connect_ssh("host", username="user") as m:
        assert(":url" in m.server_capabilities)
        with m.locked("running"):
            m.copy_config(source="running", target="file:///new_checkpoint.conf")
            m.copy_config(source="file:///old_checkpoint.conf", target="running")

Contents:

.. toctree::
    
    manager
    api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
