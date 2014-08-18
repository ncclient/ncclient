#! /usr/bin/env python2.6
#
# Connect to the NETCONF server passed on the command line and
# display their capabilities. This script and the following scripts
# all assume that the user calling the script is known by the server
# and that suitable SSH keys are in place. For brevity and clarity
# of the examples, we omit proper exception handling.
#
# $ ./nc01.py broccoli

import sys

from ncclient import manager

filter_vlan_snippet = """
<vlan xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
</vlan>"""


def create_vlan(mgr, vlanid, vlanname):
    snippet = """
<vlan xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
    <vlans>
        <vlan>
            <vlanId>%s</vlanId>
            <vlanName/>
            <vlanDesc>%s</vlanDesc>
        </vlan>
    </vlans>
</vlan>"""
    confstr = snippet % (vlanid, vlanname)
    mgr.edit_config(target='running', config=confstr)


def test_huawei_api(host, user, password):
    device = {"name": "huawei"}
    with manager.connect(host, port=830, user=user, password=password, device_params=device) as m:
        create_vlan(m, '20', 'customer')
        result = m.get_config(source="running", filter=("subtree", filter_vlan_snippet))
        print result

if __name__ == '__main__':
    test_huawei_api(sys.argv[1], sys.argv[2], sys.argv[3])
