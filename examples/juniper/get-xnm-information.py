#!/usr/bin/env python
import logging
import os

from ncclient import manager
from ncclient.xml_ import *


def connect(host, port, user, password):
    conn = manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           timeout=1800,
                           device_params={'name': 'junos'},
                           hostkey_verify=False)

    # https://www.juniper.net/documentation/en_US/junos/topics/task/operational/junos-xml-protocol-requesting-xml-schema.html
    logging.info("Requesting an XML Schema for the Configuration Hierarchy")
    logging.info("This may take several (even 10+) minutes")

    rpc = """
    <get-xnm-information>
        <type>xml-schema</type>
        <namespace>junos-configuration</namespace>
    </get-xnm-information>"""

    result = conn.rpc(rpc)
    with open('schema.txt', 'w') as fh:
        # Note: using NCElement's __str__() for python version independent conversion to string
        fh.write(str(result))
        logging.info('schema.txt is written to directory %s', os.getcwd())


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', 830, 'netconf', 'juniper!')
