#!/usr/bin/env python
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

    load_config_result = conn.load_configuration(format='text', config=location)
    logging.info(load_config_result)

    # configuration as an argument
    load_config_result = conn.load_configuration(format='text', config="""
    system {
        host-name %s;
    }
    """ % new_host_name)
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
