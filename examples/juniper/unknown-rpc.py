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


    result = conn.get_software_information('brief', test='me')
    print result.tostring

    result = conn.get_chassis_inventory('extensive')
    print result.tostring

if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!', 'candidate')
