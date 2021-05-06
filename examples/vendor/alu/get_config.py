#!/usr/bin/env python

import logging

from lxml import etree
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


    logging.info('Retrieving full config, please wait ...')

    result = conn.get_configuration()
    logging.info(result)

    logging.info('Here is the chassis configuration')
    output = result.xpath('data/configure/system/chassis')[0]
    logging.info(to_xml(output))

    logging.info('Retrieving service config')

    # specify filter to pass to get_config
    filter = new_ele('configure', attrs={'xmlns': ALU_CONFIG})
    sub_ele(filter, 'service')
    result = conn.get_configuration(filter=filter)
    epipes = result.xpath('data/configure/service/epipe')

    for i in epipes:
        logging.info(etree.tostring(i, pretty_print=True).decode('utf-8'))

    logging.info('Getting CLI -config')
    cli_cfg = conn.get_configuration(content='cli', filter=['port 1/1/11'])
    logging.info(cli_cfg)

    logging.info('Get detailed CLI -config')
    cli_cfg = conn.get_configuration(content='cli', filter=['port 1/1/11'], detail=True)
    logging.info(cli_cfg)

    conn.close_session()


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('localhost', 830, 'admin', 'admin')
