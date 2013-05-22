ncclient: Python library for NETCONF clients
--------------------------------------------

`ncclient` is a Python library that facilitates client-side scripting
and application development around the NETCONF protocol. `ncclient` was
developed by [Shikar Bhushan](http://schmizz.net). It is now maintained
by [Leonidas Poulopoulos](http://ncclient.grnet.gr)

This is a [Juniper Networks](http://www.juniper.net) fork of `ncclient` based
off of [leopoul/ncclient v0.3.2](https://github.com/leopoul/ncclient)

Requirements:
* Python 2.6 <= version < 3.0
* setuptools 0.6+
* Paramiko 1.7+
* lxml 3.0+

Installation:

    [ncclient] $ sudo python setup.py install

Usage:

    [ncclient] $ python examples/juniper/*.py
