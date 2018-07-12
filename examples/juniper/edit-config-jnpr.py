#!/usr/bin/env python
import logging
import time

from ncclient import manager
from ncclient.xml_ import *


def connect(host, port, user, password, source):
    conn = manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           timeout=60,
                           device_params={'name': 'junos'},
                           hostkey_verify=False)

    logging.info('locking configuration')
    lock_result = conn.lock()
    logging.info(lock_result)

    # build configuration element
    config = new_ele('system')
    sub_ele(config, 'host-name').text = 'foo'
    sub_ele(config, 'domain-name').text = 'bar'

    load_config_result = conn.load_configuration(config=config)
    logging.info(load_config_result)

    validate_result = conn.validate()
    logging.info(validate_result)

    compare_config_result = conn.compare_configuration()
    logging.info(compare_config_result)

    logging.info('commit confirmed')
    commit_config = conn.commit(confirmed=True, timeout='300')
    logging.info(commit_config)

    logging.info('sleeping for 5 sec...')
    time.sleep(5)

    discard_changes_result = conn.discard_changes()
    logging.info(discard_changes_result)

    logging.info('unlocking configuration')
    unlock_result = conn.unlock()
    logging.info(unlock_result)


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', 830, 'netconf', 'juniper!', 'candidate')
