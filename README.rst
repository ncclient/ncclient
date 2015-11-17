ncclient: Python library for NETCONF clients
--------------------------------------------

ncclient is a Python library that facilitates client-side scripting and
application development around the NETCONF protocol. ``ncclient`` was
developed by `Shikar Bhushan <http://schmizz.net>`_. It is now
maintained by `Leonidas Poulopoulos (@leopoul) <http://ncclient.org/ncclient>`_

Docs:
`http://ncclient.readthedocs.org <http://ncclient.readthedocs.org>`_

Requirements:
^^^^^^^^^^^^^

-  Python 2.6 <= version < 3.0
-  setuptools 0.6+
-  Paramiko 1.7+
-  lxml 3.0+
-  libxml2
-  libxslt

If you are on Debian/Ubuntu install the following libs (via aptitude or
apt-get):

-  libxml2-dev
-  libxslt1-dev

Installation:
^^^^^^^^^^^^^

::

    [ncclient] $ sudo python setup.py install

or via pip:

::

    pip install ncclient

Examples:
^^^^^^^^^

::

    [ncclient] $ python examples/juniper/*.py

Usage
~~~~~

Get device running config
'''''''''''''''''''''''''

Use either an interactive Python console (ipython) or integrate the
following in your code:

::

    from ncclient import manager

    with manager.connect(host=host, port=830, username=user, hostkey_verify=False) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

As of 0.4.1 ncclient integrates Juniper's and Cisco's forks, lots of new concepts
have been introduced that ease management of Juniper and Cisco devices respectively.
The biggest change is the introduction of device handlers in connection paramms.
For example to invoke Juniper's functions annd params one has to re-write the above with 
**device\_params={'name':'junos'}**:

::

    from ncclient import manager

    with manager.connect(host=host, port=830, username=user, hostkey_verify=False, device_params={'name':'junos'}) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

Device handlers are easy to implement and prove to be futureproof.

Supported device handlers
'''''''''''''''''''''''''

* Juniper: device_params={'name':'junos'}
* Cisco CSR: device_params={'name':'csr'}
* Cisco Nexus: device_params={'name':'nexus'}
* Huawei: device_params={'name':'huawei'}
* Alcatel Lucent: device_params={'name':'alu'}
* H3C: device_params={'name':'h3c'}
* HP Comware: device_params={'name':'hpcomware'}

Changes \| brief
~~~~~~~~~~~~~~~~

**v0.4.6**

- Fix multiple RPC error generation
- Add support for cancel-commit and persist param
- Add more examples

**v0.4.5**

- Add Huawei device support
- Add cli command support for hpcomware v7 devices
- Add H3C support, Support H3C CLI,Action,Get_bulk,Save,Rollback,etc.
- Add alcatel lucent support

- Rewrite multiple error handling
- Add coveralls support, with shield in README.md
- Set severity level to higher when multiple
- Simplify logging and multi-error reporting
- Keep stacktrace of errors
- Check for known hosts on hostkey_verify only
- Add check for device sending back null error_text
- Fix RPC.raise_mode
- Specifying hostkey_verify=False should not load_known_hosts
- Check the correct field on rpc-error element

**v0.4.3**

- Nexus exec_command operation
- Allow specifying multiple cmd elements in Cisco Nexus
- Update rpc for nested rpc-errors
- Prevent race condition in threading
- Prevent hanging in session close

**v0.4.2**

- Support for paramiko ProxyCommand via ~/.ssh/config parsing
- Add Juniper-specific commit operations
- Add Huawei devices support
- Tests/Travis support
- ioproc transport support for Juniper devices
- Update Cisco CSR device handler
- Many minor and major fixes

**v0.4.1**

-  Switch between replies if custom handler is found
-  Add Juniper, Cisco and default device handlers
-  Allow preferred SSH subsystem name in device params
-  Allow iteration over multiple SSH subsystem names.




Acknowledgements
~~~~~~~~~~~~~~~~

- v0.4.6: Thanks to all contribs and bug hunters; `Nitin Kumar <https://github.com/vnitinv>`_, `Carl Moberg <https://github.com/cmoberg>`_, `Stavros Kroustouris <https://github.com/kroustou>`_ .
- v0.4.5: Thanks to all contribs and bug hunters; `Sebastian Wiesinger <https://github.com/sebastianw>`_, `Vincent Bernat <https://github.com/vincentbernat>`_, `Matthew Stone <https://github.com/bigmstone>`_, `Nitin Kumar <https://github.com/vnitinv>`_.
- v0.4.3: Thanks to all contributors and bug hunters; `Jeremy Schulman <https://github.com/jeremyschulman>`_, `Ray Solomon <https://github.com/rsolomo>`_, `Rick Sherman <https://github.com/shermdog>`_, `subhak186 <https://github.com/subhak186>`_.
- v0.4.2: Thanks to all contributors; `katharh <https://github.com/katharh>`_, `Francis Luong (Franco) <https://github.com/francisluong>`_, `Vincent Bernat <https://github.com/vincentbernat>`_, `Juergen Brendel <https://github.com/juergenbrendel>`_, `Quentin Loos <https://github.com/Kent1>`_, `Ray Solomon <https://github.com/rsolomo>`_, `Sebastian Wiesinger <https://github.com/sebastianw>`_, `Ebben Aries <https://github.com/earies>`_ .
- v0.4.1: Many thanks, primarily to `Jeremy Schulman <https://github.com/jeremyschulman>`_ (Juniper) for providing his precious feedback, to `Eben Aries <https://github.com/earies>`_ (Juniper) for his contribution, to Juergen Brendel (Cisco) for the Cisco fork and to all contributors from Cisco and Juniper.

