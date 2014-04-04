#!/usr/bin/env python

from ncclient import manager
from ncclient.transport import errors


def connect(host, port, user, password, source):
    try:
        conn = manager.connect(host=host,
                port=port,
                username=user,
                password=password,
                timeout=10,
                device_params = {'name':'junos'},
            hostkey_verify=False)

        print 'connected:', conn.connected, ' .... to host', host, 'on port:', port
        print 'session-id:', conn.session_id
        print 'client capabilities:'
        for i in conn.client_capabilities:
            print ' ', i
        print 'server capabilities:'
        for i in conn.server_capabilities:
            print ' ', i
        conn.close_session()
    except errors.SSHError:
        print 'Unable to connect to host:', host, 'on port:', port


if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!', 'candidate')
    connect('router', 831, 'netconf', 'juniper!', 'candidate')
    connect('router', 830, 'netconf', 'juniper!', 'candidate')
