#! /usr/bin/env python
#
# Create a new user to the running configuration using edit-config
# and the test-option provided by the :validate capability.
#
# $ ./nc04.py broccoli bob 42 42

import sys, os, warnings
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager

def demo(host, user, name, uid, gid):
    snippet = """<nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
      <aaa xmlns="http://tail-f.com/ns/aaa/1.1">
        <authentication> <users> <user nc:operation="create">
        <name>%s</name> <uid>%s</uid> <gid>%s</gid>
        <password>*</password> <ssh_keydir/> <homedir/>
      </user></users></authentication></aaa></nc:config>""" % (name, uid, gid)

    with manager.connect(host=host, port=22, username=user) as m:
        assert(":validate" in m.server_capabilities)
        m.edit_config(target='running', config=snippet,
                      test_option='test-then-set')

if __name__ == '__main__':
    demo(sys.argv[1], os.getenv("USER"), sys.argv[2], sys.argv[3], sys.argv[4])
