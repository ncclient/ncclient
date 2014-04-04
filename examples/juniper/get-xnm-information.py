#!/usr/bin/env python

from ncclient import manager
from ncclient.xml_ import *

def connect(host, port, user, password, source):
    conn = manager.connect(host=host,
            port=port,
            username=user,
            password=password,
            timeout=600,
            device_params = {'name':'junos'},
            hostkey_verify=False)

    rpc = """
    <get-xnm-information>
        <type>xml-schema</type>
        <namespace>junos-configuration</namespace>
    </get-xnm-information>"""

    result = conn.rpc(rpc)
    fh = open('schema.txt', 'w')
    fh.write(result.tostring)
    fh.close()



if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!', 'candidate')
