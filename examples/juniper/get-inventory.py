#!/usr/bin/env python

from ncclient import manager

def connect(host, port, user, password):
    conn = manager.connect(host=host,
            port=port,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)


    result = conn.get_chassis_inventory()
    print "Chassis:", result.xpath('//chassis/description')[0].text
    print "Chassis Serial-Number:", result.xpath('//chassis/serial-number')[0].text

if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!')
