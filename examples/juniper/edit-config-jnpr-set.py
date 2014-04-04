#!/usr/bin/env python

from ncclient import manager

def connect(host, user, password):
    conn = manager.connect(host=host,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)

    conn.lock()

    # configuration as a string
    send_config = conn.load_configuration(action='set', config='set system host-name foo')

    # configuration as a list
    location = []
    location.append('set system location building "Main Campus, C"')
    location.append('set system location floor 15')
    location.append('set system location rack 1117')

    send_config = conn.load_configuration(action='set', config=location)
    print send_config.tostring

    check_config = conn.validate()
    print check_config.tostring

    compare_config = conn.compare_configuration()
    print compare_config.tostring

    conn.commit()
    conn.unlock()
    conn.close_session()

if __name__ == '__main__':
    connect('router', 'netconf', 'juniper!')
