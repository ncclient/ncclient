ncclient: Python library for NETCONF clients
--------------------------------------------

ncclient is a Python library that facilitates client-side scripting and
application development around the NETCONF protocol. ``ncclient`` was
developed by `Shikar Bhushan <http://schmizz.net>`_. It is now
maintained by `Leonidas Poulopoulos (@leopoul) <http://ncclient.org>`_

Docs:
`http://ncclient.readthedocs.org <http://ncclient.readthedocs.org>`_

Github:
`https://github.com/ncclient/ncclient <https://github.com/ncclient/ncclient>`_

Requirements:
^^^^^^^^^^^^^

-  Python >= 2.6 or Python 3
-  setuptools 0.6+
-  Paramiko 1.7+
-  lxml 3.3.0+
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

**v0.5.3**

- Add notifications support
- Add support for ecdsa keys
- Various bug fixes

**v0.5.2**

- Add support for Python 3
- Improve Junos ioproc performance
- Performance improvements
- Updated test cases
- Many bug and performance fixes


**v0.4.7**

- Add support for netconf 1.1

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

-  v0.5.3: `Justin Wilcox`_, `Stacy W. Smith`_, `Mircea Ulinic`_,
   `Ebben Aries`_, `Einar Nilsen-Nygaard`_, `QijunPan`_
-  v0.5.2: `Nitin Kumar`_, `Kristian Larsson`_, `palashgupta`_,
   `Jonathan Provost`_, `Jainpriyal`_, `sharang`_, `pseguel`_,
   `nnakamot`_, `Алексей Пастухов`_, `Christian Giese`_, `Peipei Guo`_,
   `Time Warner Cable Openstack Team`_
-  v0.4.7: `Einar Nilsen-Nygaard`_, `Vaibhav Bajpai`_, Norio Nakamoto
-  v0.4.6: `Nitin Kumar`_, `Carl Moberg`_, `Stavros Kroustouris`_
-  v0.4.5: `Sebastian Wiesinger`_, `Vincent Bernat`_, `Matthew Stone`_,
   `Nitin Kumar`_
-  v0.4.3: `Jeremy Schulman`_, `Ray Solomon`_, `Rick Sherman`_,
   `subhak186`_
-  v0.4.2: `katharh`_, `Francis Luong (Franco)`_, `Vincent Bernat`_,
   `Juergen Brendel`_, `Quentin Loos`_, `Ray Solomon`_, `Sebastian
   Wiesinger`_, `Ebben Aries`_
-  v0.4.1: `Jeremy Schulman`_, `Ebben Aries`_, Juergen Brendel

.. _Nitin Kumar: https://github.com/vnitinv
.. _Kristian Larsson: https://github.com/plajjan
.. _palashgupta: https://github.com/palashgupta
.. _Jonathan Provost: https://github.com/JoProvost
.. _Jainpriyal: https://github.com/Jainpriyal
.. _sharang: https://github.com/sharang
.. _pseguel: https://github.com/pseguel
.. _nnakamot: https://github.com/nnakamot
.. _Алексей Пастухов: https://github.com/p-alik
.. _Christian Giese: https://github.com/GIC-de
.. _Peipei Guo: https://github.com/peipeiguo
.. _Time Warner Cable Openstack Team: https://github.com/twc-openstack
.. _Einar Nilsen-Nygaard: https://github.com/einarnn
.. _Vaibhav Bajpai: https://github.com/vbajpai
.. _Carl Moberg: https://github.com/cmoberg
.. _Stavros Kroustouris: https://github.com/kroustou
.. _Sebastian Wiesinger: https://github.com/sebastianw
.. _Vincent Bernat: https://github.com/vincentbernat
.. _Matthew Stone: https://github.com/bigmstone
.. _Jeremy Schulman: https://github.com/jeremyschulman
.. _Ray Solomon: https://github.com/rsolomo
.. _Rick Sherman: https://github.com/shermdog
.. _subhak186: https://github.com/subhak186
.. _katharh: https://github.com/katharh
.. _Francis Luong (Franco): https://github.com/francisluong
.. _Juergen Brendel: https://github.com/juergenbrendel
.. _Quentin Loos: https://github.com/Kent1
.. _Ebben Aries: https://github.com/earies
.. _Justin Wilcox: https://github.com/jwwilcox
.. _Stacy W. Smith: https://github.com/stacywsmith
.. _Mircea Ulinic: https://github.com/mirceaulinic
.. _QijunPan: https://github.com/QijunPan
