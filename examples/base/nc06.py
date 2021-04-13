#! /usr/bin/env python
#
# Delete a list of existing users from the running configuration using
# edit-config; protect the transaction using a lock.
#
# $ ./nc06.py broccoli bob alice

import sys, os, warnings
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager

template = """<nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <aaa xmlns="http://tail-f.com/ns/aaa/1.1">
  <authentication> <users> <user nc:operation="delete">
  <name>%s</name> </user></users></authentication></aaa></nc:config>"""

def demo(host, user, names):
    with manager.connect(host=host, port=22, username=user) as m:
        with m.locked(target='running'):
            for n in names:
                m.edit_config(target='running', config=template % n)

if __name__ == '__main__':
    demo(sys.argv[1], os.getenv("USER"), sys.argv[2:])
