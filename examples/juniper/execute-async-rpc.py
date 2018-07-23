import logging

from ncclient import manager
from ncclient.xml_ import *
import time
from ncclient.devices.junos import JunosDeviceHandler


def connect(host, port, user, password):
    conn = manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           timeout=60,
                           device_params={'name': 'junos'},
                           hostkey_verify=False)

    junos_dev_handler = JunosDeviceHandler(
        device_params={'name': 'junos',
                       'local': False})

    conn.async_mode = True

    rpc = new_ele('get-software-information')
    obj = conn.rpc(rpc)

    # for demo purposes, we just wait for the result 
    while not obj.event.is_set():
        logging.info('waiting for answer ...')
        time.sleep(.3)

    result = NCElement(obj.reply,
                       junos_dev_handler.transform_reply()
                       ).remove_namespaces(obj.reply.xml)

    logging.info('Hostname: %s', result.findtext('.//host-name'))


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    connect('router', 830, 'netconf', 'juniper!')
