#!/usr/bin/env python
import logging

from ncclient import manager
from ncclient.xml_ import *


def connect(host, port, user, password):
    conn = manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           timeout=10,
                           device_params={'name': 'alu'},
                           hostkey_verify=False)

    print('Set CLI -config -block')

    config = """
    configure port 1/1/1
        description \"Loaded as CLI -block\"
    exit"""

    conn.load_configuration(format='cli', config=config)


    print('Load XML -config')
    config = new_ele('configure', attrs={'xmlns': ALU_CONFIG})
    port = sub_ele(config, 'port')
    sub_ele(port, 'port-id').text = '1/1/1'
    desc = sub_ele(port, 'description')
    sub_ele(desc, 'long-description-string').text = "Loaded using XML"

    conn.load_configuration(config=config, format='xml')

    conn.close_session()

if __name__ == '__main__':
    connect('router', 830, 'admin', 'admin')
