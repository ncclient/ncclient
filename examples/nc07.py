#! /usr/bin/env python2.6 
#
# Delete a list of existing users from the running configuration using
# edit-config and the candidate datastore protected by a lock.
#
# $ ./nc07.py broccoli bob alice

import sys, os, warnings
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager

template = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <aaa xmlns="http://tail-f.com/ns/aaa/1.1">
  <authentication> <users> <user xc:operation="delete">
  <name>%s</name> </user></users></authentication></aaa></config>"""

def demo(host, user, names):
    with manager.connect(host=host, port=22, username=user) as m:
        assert(":candidate" in m.server_capabilities)
        with m.locked(target='candidate'):
            m.discard_changes()
            for n in names:
                m.edit_config(target='candidate', config=template % n)
            m.commit()

if __name__ == '__main__':
    demo(sys.argv[1], os.getenv("USER"), sys.argv[2:])
