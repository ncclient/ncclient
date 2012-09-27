#! /usr/bin/env python2.6 
#
# Retreive configuration from the candidate datastore after performing
# a discard-changes on it.
#
# $ ./nc08.py broccoli

import sys, os, warnings, logging
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager

def demo(host, user, names):
    with manager.connect(host=host, port=830, username='vagrant', password='vagrant') as m:
        assert(":candidate" in m.server_capabilities)
        with m.locked(target='candidate'):
            m.discard_changes()
            c = m.get_config('candidate').data_xml
            with open("%s.xml" % host, 'w') as f:
                f.write(c)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    demo(sys.argv[1], os.getenv("USER"), sys.argv[2:])
