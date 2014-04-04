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

    # configuration as a text string
    host_name = """
    system {
        host-name foo-bar;
    }
    """

    send_config = conn.edit_config(format='text', config=host_name)
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
