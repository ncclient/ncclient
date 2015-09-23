#!/usr/bin/env python

from ncclient import manager
from ncclient.xml_ import *
from getpass import getpass


def connect(host, user, password):
    with manager.connect(
        host=host,
        port=22,
        username=user,
        password=password,
        timeout=10,
        device_params={'name': 'junos'},
        hostkey_verify=False
    ) as conn:
        vpns = conn.command(
            'show l2circuit connections'
        ).xpath(
            'l2circuit-connection-information/l2circuit-neighbor'
        )
        connection_dict = {}
        for vpn in vpns:
            neighbor = ''
            for tag in vpn.getchildren():
                connection_details_dict = {}
                if tag.tag == 'neighbor-address':
                    neighbor = tag.text
                if tag.tag == 'connection':
                    for child in tag.getchildren():
                        if child.tag == 'local-interface':
                            ifce = child.find('interface-name').text
                            connection_details_dict.update({'interface': ifce})
                        else:
                            if child.tag == 'connection-id':
                                cid = child.text
                            else:
                                connection_details_dict.update({child.tag: child.text})
                    connection_details_dict.update({'neighbor': neighbor})
                    if connection_dict.get(cid):
                        connection_dict.get(cid).append(connection_details_dict)
                    else:
                        connection_dict.update({cid: [connection_details_dict]})

    return connection_dict

if __name__ == '__main__':
    host = 'router.example.com'
    username = raw_input('Give the username for %s: ' % host)
    password = getpass.getpass('Give the password: ')
    response = connect(host, username, p)
