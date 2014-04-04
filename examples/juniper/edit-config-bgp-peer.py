#!/usr/bin/env python

import logging

from ncclient import manager
from ncclient.xml_ import *

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)

def connect(host, port, user, password, source):
    conn = manager.connect(host=host,
            port=port,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)

    print 'locking configuration'
    lock = conn.lock()

    peers = {
            '10.1.1.1':'65001',
            '10.2.1.1':'65002',
            '10.3.1.1':'65003',
            '10.4.1.1':'65004',
            '10.5.1.1':'65005'
            }

    # build configuration element
    config = new_ele('protocols')
    config_bgp = sub_ele(config, 'bgp')
    config_group = sub_ele(config_bgp, 'group')
    config_group_name = sub_ele(config_group, 'name').text = 'NETCONF_GROUP'
    sub_ele(config_group, 'multipath')
    sub_ele(config_group, 'local-address').text = '10.0.0.1'
    for peer in peers:
        config_neighbor = sub_ele(config_group, 'neighbor')
        sub_ele(config_neighbor, 'name').text = peer
        sub_ele(config_neighbor, 'peer-as').text = peers[peer]

    send_config = conn.load_configuration(config=config)
    print send_config.tostring

    check_config = conn.validate()
    print check_config.tostring

    compare_config = conn.compare_configuration()
    print compare_config.tostring

    commit_config = conn.commit()
    print 'committed configuration'


    discard_changes = conn.discard_changes()
    print discard_changes.tostring

    print 'unlocking configuration'
    unlock = conn.unlock()
    print unlock.tostring

if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!', 'candidate')
