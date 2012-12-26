
ncclient: Python library for NETCONF clients
--------------------------------------------

`ncclient` is a Python library that facilitates client-side scripting
and application development around the NETCONF protocol. `ncclient` was
developed by [Shikar Bhushan](http://schmizz.net). It is now maintained
by [Leonidas Poulopoulos](http://ncclient.grnet.gr)

This is a [CNDS](http://cnds.eecs.jacobs-university.de) fork of
`ncclient`. We have added NETCONF v1.1 support, that allows `ncclient`
to handle chunked frames [RFC 6242]. The client fallsback to NETCONF
v1.0 end of message frames [RFC 4742] for legacy servers that do not
advertise NETCONF v1.1 capability. We have updated the example scripts
to accept positional and optional arguments to allow the same script to
talk to multiple server implementations. We tested the implementation at
the NETCONF interoperability testing event at [IETF 85,
Atlanta](http://www.ietf.org/meeting/85/). `ncclient` was tested with
[ConfD](http://www.tail-f.com/products-and-services/confd),
[Yuma](http://www.yumaworks.com/yuma/) and
[libnetconf](http://code.google.com/p/libnetconf/) servers. This fork is
maintained by [Vaibhav Bajpai](http://vaibhavbajpai.com). 

Requirements:  
* Python 2.6 <= version < 3.0  
* Paramiko 1.7.7.1+  

Installation:

    [ncclient] $ mkvirtualenv ncclient
    [ncclient] $ make

Usage:

    [ncclient] $ python examples/ncXX.py 
