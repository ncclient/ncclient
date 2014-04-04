#!/usr/bin/env python

from ncclient import manager
from ncclient.xml_ import *

import time

def connect(host, port, user, password, source):
    conn = manager.connect(host=host,
            port=port,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)

    rpc = new_ele('get-software-information')

    result = conn.rpc(rpc)
    print 'Hostname:', result.xpath('//software-information/host-name')[0].text

if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!', 'candidate')
