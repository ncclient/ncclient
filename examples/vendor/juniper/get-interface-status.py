#!/usr/bin/env python
# Python script to fetch interface name and their operation status
import sys

import logging

from ncclient import manager


def connect(host, port, user, password):
    conn = manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           timeout=60,
                           device_params={'name': 'junos'},
                           hostkey_verify=False)

    rpc = "<get-interface-information><terse/></get-interface-information>"
    response = conn.rpc(rpc)
    interface_name = response.xpath('//physical-interface/name')
    interface_status = response.xpath('//physical-interface/oper-status')
    for name, status in zip(interface_name, interface_status):
        name = name.text.split('\n')[1]
        status = status.text.split('\n')[1]
        logging.info("{} - {}".format(name, status))


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', 830, 'netconf', 'juniper!')

