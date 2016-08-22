#!/usr/bin/env python

import json

from ncclient import manager

def connect(host, user, password):
    conn = manager.connect(host=host,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)

    conn.lock()

    # configuration as a json encoded string
    location = """
    {
        "configuration": {
            "system": {
                "location": {
                    "building": "Main Campus, E",
                    "floor": "15"
                }
            }
        }
    }
    """

    config_json = json.loads(location)
    config_json['configuration']['system']['location']['rack'] = "1117"
    config = json.dumps(config_json)

    send_config = conn.load_configuration(format='json', config=config)
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
