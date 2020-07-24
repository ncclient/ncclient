Welcome
=======

`ncclient` is a Python library for NETCONF clients. It aims to offer an intuitive API that sensibly maps the XML-encoded nature of NETCONF to Python constructs and idioms, and make writing network-management scripts easier. Other key features are:

* Supports all operations and capabilities defined in :rfc:`6241`.
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
For example to invoke Juniper's functions and params one has to re-write the above with **device_params={'name':'junos'}**::

    from ncclient import manager

    with manager.connect(host=host, port=830, username=user, hostkey_verify=False, device_params={'name':'junos'}) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

Respectively, for Cisco Nexus, the name is **nexus**.
Device handlers are easy to implement and prove to be futureproof.

The latest pull request merge includes support for Huawei devices with name **huawei** in device_params.

Supported device handlers
-------------------------
* Juniper: `device_params={'name':'junos'}`
* Cisco:
    - CSR: `device_params={'name':'csr'}`
    - Nexus: `device_params={'name':'nexus'}`
    - IOS XR: `device_params={'name':'iosxr'}`
    - IOS XE: `device_params={'name':'iosxe'}`
* Huawei:
    - `device_params={'name':'huawei'}`
    - `device_params={'name':'huaweiyang'}`
* Alcatel Lucent: `device_params={'name':'alu'}`
* H3C: `device_params={'name':'h3c'}`
* HP Comware: `device_params={'name':'hpcomware'}`
* Server or anything not in above: `device_params={'name':'default'}`


Contents:

.. toctree::

    manager
    api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
