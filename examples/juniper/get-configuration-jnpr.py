#!/usr/bin/env python

import json
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

    result_xml = conn.get_configuration(format='xml')
    logging.info(result_xml)

    result_json = conn.get_configuration(format='json')
    payload = json.loads(result_json.xpath('.')[0].text)
    logging.info(payload)
    logging.info(payload['configuration'][0]['system'][0]['services'])

    result_text = conn.get_configuration(format='text')
    logging.info(result_text.xpath('configuration-text')[0].text)

    logging.info('Version')
    logging.info('*' * 30)
    logging.info(result_xml.xpath('configuration/version')[0].text)

    config_filter = new_ele('configuration')
    system_ele = sub_ele(config_filter, 'system')
    sub_ele(system_ele, 'login')

    result_filter = conn.get_configuration(format='xml', filter=config_filter)
    logging.info(result_filter)

    logging.info('Configured Interfaces...')
    interfaces = result_xml.xpath('configuration/interfaces/interface')
    for i in interfaces:
        interface = i.xpath('name')[0].text
        ip = []
        for name in i.xpath('unit/family/inet/address/name'):
            ip.append(name.text)
        logging.info(' %s %s', interface, ip)


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', 830, 'netconf', 'juniper!')
