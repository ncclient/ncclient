#!/usr/bin/env python
from ncclient import manager
import getpass


def connect(host, port, user, password, command):
    with manager.connect(
        host=host,
        port=port,
        username=user,
        password=password,
        timeout=10,
        device_params={'name': 'junos'},
        hostkey_verify=False
    ) as m:
        with m.locked():
            m.load_configuration(action='set', config=command)
            result = m.commit()
            print result


if __name__ == '__main__':
    host = 'router.example.com'
    username = raw_input('Give the username for %s: ' % host)
    password = getpass.getpass('Give the password: ')
    interface = 'em0'
    connect(host, 830, username, password, 'set interfaces %s description example' % interface)
