#!/usr/bin/env python
import logging

from ncclient import manager
from ncclient.xml_ import *


def connect(host, port, user, password):
    conn = manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           timeout=60,
                           device_params={'name': 'junos'},
                           hostkey_verify=False)

    template = """<system><scripts><commit>
<file delete="delete"><name>test.slax</name></file>
</commit></scripts></system>"""

    conn.lock()
    config = to_ele(template)
    load_config_result = conn.load_configuration(config=config)
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

    connect('router', 830, 'netconf', 'juniper!')
