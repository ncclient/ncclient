[![Build Status](https://travis-ci.org/leopoul/ncclient.svg?branch=master)](https://travis-ci.org/leopoul/ncclient)

ncclient: Python library for NETCONF clients
--------------------------------------------

ncclient is a Python library that facilitates client-side scripting
and application development around the NETCONF protocol. `ncclient` was
developed by [Shikar Bhushan](http://schmizz.net). It is now maintained
by [Leonidas Poulopoulos (@leopoul)](http://ncclient.grnet.gr)

This version includes a merge of [Juniper Networks](http://www.juniper.net)
and [Cisco Systems](http://www.cisco.com) respective ncclient forks based
on [leopoul/ncclient v0.3.2](https://github.com/leopoul/ncclient)

**Docs**: [http://ncclient.readthedocs.org](http://ncclient.readthedocs.org)

**PyPI**: [https://pypi.python.org/pypi/ncclient](https://pypi.python.org/pypi/ncclient)

#### Requirements:
* Python 2.6 <= version < 3.0
* setuptools 0.6+
* Paramiko 1.7+
* lxml 3.0+
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
#####Get device running config
Use either an interactive Python console (ipython)
or integrate the following in your code:

    from ncclient import manager

    with manager.connect(host=host, port=830, username=user, hostkey_verify=False) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

As this version integrates Juniper's and Cisco's forks, lots of new concepts
have been introduced that ease management of Juniper and Cisco devices respectively.
The biggest change is the introduction of device handlers in connection paramms.
For example to invoke Juniper's functions annd params one has to re-write the above with ***device_params={'name':'junos'}***:

    from ncclient import manager

    with manager.connect(host=host, port=830, username=user, hostkey_verify=False, device_params={'name':'junos'}) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

Respectively, for Cisco nxos, the name is **nxos**.
Device handlers are easy to implement and prove to be futureproof.

### Changes | brief
* Switch between replies if custom handler is found
* Add Juniper, Cisco and default device handlers
* Allow preferred SSH subsystem name in device params
* Allow iteration over multiple SSH subsystem names.

### Acknowledgements
Many thanks, primarily to [Jeremy Schulman](https://github.com/jeremyschulman) (Juniper) for providing his precious feedback,
to [Ebben Aries](https://github.com/earies) (Juniper) for his contribution, to Juergen Brendel (Cisco) for the Cisco fork and
to all contributors from Cisco and Juniper.
