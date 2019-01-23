#!/usr/bin/env python
import json
import logging
import sys

from ncclient import manager


def connect(host, port, user, password):
    conn = manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           timeout=60,
                           device_params={'name': 'junos'},
                           hostkey_verify=False)

    conn.lock()

    # configuration as a json encoded string
    # TODO: this example (and possibly the ncclient library implementation?) is broken!
    # class LoadConfiguration in operations/third_party/juniper/rpc.py would expect 'configuration-json' element to be
    # used. Changing "configuration" to "configuration-json" in the 2 occasions below: still does not work!
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

    load_config_result = conn.load_configuration(format='json', config=config)
    logging.info(load_config_result)

    validate_result = conn.validate()
    logging.info(validate_result)

    compare_config_result = conn.compare_configuration()
    logging.info(compare_config_result)

    conn.commit()
    conn.unlock()
    conn.close_session()


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', '22', 'netconf', 'juniper!')
