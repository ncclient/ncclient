#!/usr/bin/env python
import logging

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

    logging.info('Retrieving full config, please wait ...')
    result = conn.get_config(source)

    logging.info('Showing \'system\' hierarchy ...')
    output = result.xpath('data/configuration/system')[0]
    logging.info(to_xml(output))

    # specify filter to pass to get_config
    root_filter = new_ele('filter')
    config_filter = sub_ele(root_filter, 'configuration')
    system_filter = sub_ele(config_filter, 'system')
    sub_ele(system_filter, 'services')
    
    filtered_result = conn.get_config(source, filter=root_filter)
    logging.info('Configured Services...')
    for i in filtered_result.xpath('data/configuration/system/services/*'):
        logging.info(' %s', i.tag)

    logging.info('Configured Interfaces...')
    logging.info('%-15s %-30s' % ('Name', 'Description'))
    logging.info('-' * 40)
    interfaces = result.xpath('data/configuration/interfaces/interface')
    for i in interfaces:
        if i.tag == 'interface':
            interface = i.xpath('name')[0].text
            try:
                description = i.xpath('description')[0].text
            except IndexError:
                description = None
            logging.info('%-15s %-30s' % (interface, description))
            units = i.xpath('unit')
            for u in units:
                unit = u.xpath('name')[0].text
                try:
                    u_desc = u.xpath('description')[0].text 
                except IndexError:
                    u_desc = None
                logging.info('   %-12s %-30s' % (unit, u_desc))


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', 830, 'netconf', 'juniper!', 'candidate')
