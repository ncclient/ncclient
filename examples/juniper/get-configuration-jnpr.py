#!/usr/bin/env python

import json

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

    result_xml = conn.get_configuration(format='xml')
    print result_xml.tostring

    result_json = conn.get_configuration(format='json')
    payload = json.loads(result_json.xpath('.')[0].text)
    print(payload['configuration']['system']['services'])

    result_text = conn.get_configuration(format='text')
    print result_text.xpath('configuration-text')[0].text

    print 'Version'
    print '*' * 30
    print result_xml.xpath('configuration/version')[0].text

    
    config_filter = new_ele('configuration')
    system_ele = sub_ele(config_filter, 'system')
    sub_ele(system_ele, 'login')

    result_filter = conn.get_configuration(format='xml', filter=config_filter)
    print result_filter.tostring

    print 'Configured Interfaces...'
    interfaces = result_xml.xpath('configuration/interfaces/interface')
    for i in interfaces:
        interface = i.xpath('name')[0].text
        ip = []
        for i in i.xpath('unit/family/inet/address/name'):
            ip.append(i.text)
        print ' ', interface, ip


if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!', 'candidate')
