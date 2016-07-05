[![Build Status](https://travis-ci.org/ncclient/ncclient.svg?branch=master)](https://travis-ci.org/ncclient/ncclient)
[![Coverage Status](https://coveralls.io/repos/github/ncclient/ncclient/badge.svg?branch=master)](https://coveralls.io/github/ncclient/ncclient?branch=master)
[![Documentation Status](https://readthedocs.org/projects/ncclient/badge/?version=latest)](https://readthedocs.org/projects/ncclient/?badge=latest)

ncclient: Python library for NETCONF clients
--------------------------------------------


ncclient is a Python library that facilitates client-side scripting
and application development around the NETCONF protocol. `ncclient` was
developed by [Shikar Bhushan](http://schmizz.net). It is now maintained
by [Leonidas Poulopoulos (@leopoul)](http://ncclient.org)

**Docs**: [http://ncclient.readthedocs.org](http://ncclient.readthedocs.org)

**PyPI**: [https://pypi.python.org/pypi/ncclient](https://pypi.python.org/pypi/ncclient)

#### Requirements:
* version >= Python 2.6 or Python3
* setuptools 0.6+
* Paramiko 1.7+
* lxml 3.3.0+
* libxml2
* libxslt

If you are on Debian/Ubuntu install the following libs (via aptitude or apt-get):
* libxml2-dev
* libxslt1-dev

#### Installation:

    [ncclient] $ sudo python setup.py install
    
or via pip:

    pip install ncclient

#### Examples:

    [ncclient] $ python examples/juniper/*.py

### Usage
####Get device running config
Use either an interactive Python console (ipython)
or integrate the following in your code:

    from ncclient import manager

    with manager.connect(host=host, port=830, username=user, hostkey_verify=False) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

As of 0.4.1 ncclient integrates Juniper's and Cisco's forks, lots of new concepts
have been introduced that ease management of Juniper and Cisco devices respectively.
The biggest change is the introduction of device handlers in connection paramms.
For example to invoke Juniper's functions annd params one has to re-write the above with ***device_params={'name':'junos'}***:

    from ncclient import manager

    with manager.connect(host=host, port=830, username=user, hostkey_verify=False, device_params={'name':'junos'}) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

Device handlers are easy to implement and prove to be futureproof.

####Supported device handlers

* Juniper: device_params={'name':'junos'}
* Cisco CSR: device_params={'name':'csr'}
* Cisco Nexus: device_params={'name':'nexus'}
* Huawei: device_params={'name':'huawei'}
* Alcatel Lucent: device_params={'name':'alu'}
* H3C: device_params={'name':'h3c'}
* HP Comware: device_params={'name':'hpcomware'}


### Changes | brief

* Python 3 support
* Bug fixes


Contributors
~~~~~~~~~~~~

-  v0.5.0: `Nitin Kumar`_, `Kristian Larsson`_, `palashgupta`_,
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
