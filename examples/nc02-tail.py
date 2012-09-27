#! /usr/bin/env python2.6 
#
# Retrieve the running config from the NETCONF server passed on the
# command line using get-config and write the XML configs to files.
#
# $ ./nc02.py broccoli

import sys, os, warnings, logging
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager

def demo(host, user, source='candidate'):
    with manager.connect(host=host, port=22, username=user) as m:
        c = m.get_config(source).data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) == 3: demo(sys.argv[1], os.getenv("USER"), sys.argv[2])
    else: demo(sys.argv[1], os.getenv("USER"))
