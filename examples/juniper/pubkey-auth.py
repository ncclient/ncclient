#!/usr/bin/env python

from ncclient import manager

def connect(host, port, user):
    conn = manager.connect(host=host,
            port=port,
            username=user,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)


    result = conn.get_software_information('brief', test='me')
    print 'Hostname:', result.xpath('software-information/host-name')[0].text

if __name__ == '__main__':
    connect('router', 22, 'earies')
