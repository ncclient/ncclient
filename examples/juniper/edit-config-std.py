#!/usr/bin/env python

from ncclient import manager
from ncclient.xml_ import new_ele, sub_ele

def connect(host, user, password):
    conn = manager.connect(host=host,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)

    conn.lock()

    root = new_ele('config')
    configuration = sub_ele(root, 'configuration')
    system = sub_ele(configuration, 'system')
    location = sub_ele(system, 'location')
    sub_ele(location, 'building').text = "Main Campus, A"
    sub_ele(location, 'floor').text = "5"
    sub_ele(location, 'rack').text = "27"

    send_config = conn.edit_config(config=root)
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
