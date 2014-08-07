Welcome
=======

`ncclient` is a Python library for NETCONF clients. It aims to offer an intuitive API that sensibly maps the XML-encoded nature of NETCONF to Python constructs and idioms, and make writing network-management scripts easier. Other key features are:

* Supports all operations and capabilities defined in :rfc:`4741`.
* Request pipelining.
* Asynchronous RPC requests.
* Keeping XML out of the way unless really needed.
* Extensible. New transport mappings and capabilities/operations can be easily added.

The best way to introduce is through a simple code example::

    from ncclient import manager

    # use unencrypted keys from ssh-agent or ~/.ssh keys, and rely on known_hosts
    with manager.connect_ssh("host", username="user") as m:
        assert(":url" in m.server_capabilities)
        with m.locked("running"):
            m.copy_config(source="running", target="file:///new_checkpoint.conf")
            m.copy_config(source="file:///old_checkpoint.conf", target="running")

As of version 0.4 there has been an integration of Juniper's and Cisco's forks. Thus, lots of new concepts
have been introduced that ease management of Juniper and Cisco devices respectively.
The biggest change is the introduction of device handlers in connection params.
For example to invoke Juniper's functions annd params one has to re-write the above with **device_params={'name':'junos'}**::

    from ncclient import manager

    with manager.connect(host=host, port=830, username=user, hostkey_verify=False, device_params={'name':'junos'}) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

Respectively, for Cisco nxos, the name is **nxos**.
Device handlers are easy to implement and prove to be futureproof.

The latest pull request merge includes support for Huawei devices with name **huawei** in device_params.

Contents:

.. toctree::

    manager
    api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
