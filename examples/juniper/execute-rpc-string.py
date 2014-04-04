#!/usr/bin/env python

from ncclient import manager
from ncclient.xml_ import *

def connect(host, port, user, password, source):
    conn = manager.connect(host=host,
            port=port,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)

    rpc = """
    <get-chassis-inventory>
        <detail/>
    </get-chassis-inventory>"""

    result = conn.rpc(rpc)
    print 'Chassis serial-number:', result.xpath('//chassis-inventory/chassis/serial-number')[0].text



if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!', 'candidate')
