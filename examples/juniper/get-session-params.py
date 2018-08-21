#!/usr/bin/env python
import logging
import sys

from ncclient import manager
from ncclient.transport import errors


def connect(host, port, user, password):
    try:
        conn = manager.connect(host=host,
                               port=port,
                               username=user,
                               password=password,
                               timeout=60,
                               device_params={'name': 'junos'},
                               hostkey_verify=False)

        logging.info('connected: %s ... to host %s on port %s', conn.connected, host, port)
        logging.info('session-id %s:', conn.session_id)
        logging.info('client capabilities:')
        for i in conn.client_capabilities:
            logging.info(' %s', i)
        logging.info('server capabilities:')
        for i in conn.server_capabilities:
            logging.info(' %s', i)
        conn.close_session()
    except errors.SSHError:
        logging.exception('Unable to connect to host: %s on port %s', host, port)


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', 830, 'netconf', 'juniper!')
    connect('router', 831, 'netconf', 'juniper!')
    connect('router', 830, 'netconf', 'juniper!')
