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

    logging.info('show system users')
    logging.info('*' * 30)
    result = conn.command(command='show system users', format='text')
    logging.info(result)

    logging.info('show version')
    logging.info('*' * 30)
    result = conn.command('show version', format='text')
    logging.info(result.xpath('output')[0].text)

    logging.info('bgp summary')
    logging.info('*' * 30)
    result = conn.command('show bgp summary')
    logging.info(result)


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', '22', 'netconf', 'juniper!')
