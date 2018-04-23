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

    rollback_config = conn.rollback(rollback=1)
    print rollback_config.tostring

if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!')
