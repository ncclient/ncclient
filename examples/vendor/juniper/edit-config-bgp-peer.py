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

    logging.info('locking configuration')
    lock_result = conn.lock()
    logging.info(lock_result)

    peers = {
            '10.1.1.1': '65001',
            '10.2.1.1': '65002',
            '10.3.1.1': '65003',
            '10.4.1.1': '65004',
            '10.5.1.1': '65005'
            }

    # build configuration element
    config = new_ele('protocols')
    config_bgp = sub_ele(config, 'bgp')
    config_group = sub_ele(config_bgp, 'group')
    # TODO: unused variable! Is this example broken?
    config_group_name = sub_ele(config_group, 'name').text = 'NETCONF_GROUP'
    sub_ele(config_group, 'multipath')
    sub_ele(config_group, 'local-address').text = '10.0.0.1'
    for peer in peers:
        config_neighbor = sub_ele(config_group, 'neighbor')
        sub_ele(config_neighbor, 'name').text = peer
        sub_ele(config_neighbor, 'peer-as').text = peers[peer]

    load_config_result = conn.load_configuration(config=config)
    logging.info(load_config_result)

    validate_result = conn.validate()
    logging.info(validate_result)

    compare_config_result = conn.compare_configuration()
    logging.info(compare_config_result)

    conn.commit()
    logging.info('committed configuration')

    discard_changes_result = conn.discard_changes()
    logging.info(discard_changes_result)

    logging.info('unlocking configuration')
    unlock_result = conn.unlock()
    logging.info(unlock_result)


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', 830, 'netconf', 'juniper!')
