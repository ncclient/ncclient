#!/usr/bin/env python
import logging
import sys
import time

from ncclient import manager


def connect(host, port, user, password):
    conn = manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           timeout=60,
                           device_params={'name': 'junos'},
                           hostkey_verify=False)

    result = conn.reboot()
    logging.info(result)
    reboot_nodes = result.xpath('request-reboot-results/request-reboot-status')
    if reboot_nodes:
        reboot_time = result.xpath('request-reboot-results/request-reboot-status/@reboot-time')[0]
        if 'Shutdown NOW' in reboot_nodes[0].text:
            logging.info('Rebooted at: %s', time.ctime(int(reboot_time)))


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', 830, 'netconf', 'juniper!')
