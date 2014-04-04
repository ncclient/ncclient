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

    new_host_name = 'foo-bar'

    # configuration as a text string
    location = """
    system {
        location {
            building "Main Campus, E";
            floor 15;
            rack 1117;
        }
    }
    """

    send_config = conn.load_configuration(format='text', config=location)
    print send_config.tostring

    # configuration as an argument
    send_config = conn.load_configuration(format='text',
            config="""
            system {
                host-name %s;
            }
            """ % (new_host_name))
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
