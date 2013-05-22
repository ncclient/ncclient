#! /usr/bin/env python2.6 
#
# Delete an existing user from the running configuration using
# edit-config and the test-option provided by the :validate
# capability.
#
# $ ./nc05.py broccoli bob

import sys, os, warnings
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager

def demo(host, user, name):
    snippet = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
      <aaa xmlns="http://tail-f.com/ns/aaa/1.1">
        <authentication> <users> <user xc:operation="delete">
        <name>%s</name>
      </user></users></authentication></aaa></config>""" % name

    with manager.connect(host=host, port=22, username=user) as m:
        assert(":validate" in m.server_capabilities)
        m.edit_config(target='running', config=snippet,
                      test_option='test-then-set')

if __name__ == '__main__':
    demo(sys.argv[1], os.getenv("USER"), sys.argv[2])
