#!/usr/bin/env python
import logging
import sys

from ncclient import manager


def connect(host, port, user):
    conn = manager.connect(host=host,
                           port=port,
                           username=user,
                           timeout=60,
                           device_params={'name': 'junos'},
                           hostkey_verify=False)

    result = conn.get_software_information('brief', test='me')
    logging.info('Hostname: %s', result.xpath('software-information/host-name')[0].text)


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', 22, 'earies')
