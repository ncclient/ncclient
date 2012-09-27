#! /usr/bin/env python2.6 
#
# Retrieve a portion selected by an XPATH expression from the running
# config from the NETCONF server passed on the command line using
# get-config and write the XML configs to files.
#
# $ ./nc03.py broccoli "aaa/authentication/users/user[name='schoenw']"

import sys, os, warnings, logging
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager

def demo(host, user, source='candidate', expr='aaa/authentication/users/user[name="schoenw"]'):
    with manager.connect(host=host, port=22, username=user) as m:
        assert(":xpath" in m.server_capabilities)
        c = m.get_config(source, filter=('xpath', expr)).data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) == 4: demo(sys.argv[1], os.getenv("USER"), sys.argv[2], sys.argv[3])
    else: demo(sys.argv[1], os.getenv("USER"))
