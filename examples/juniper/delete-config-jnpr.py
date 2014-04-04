#!/usr/bin/env python

from ncclient import manager
from ncclient.xml_ import *

def connect(host, port, user, password, source):
    conn = manager.connect(host=host,
            port=port,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)

    template = """<system><scripts><commit><file delete="delete"><name>test.slax</name></file></commit></scripts></system>"""

    conn.lock()
    config = to_ele(template)
    send_config = conn.load_configuration(config=config)
    print send_config.tostring

    check_config = conn.validate()
    print check_config.tostring

    compare_config = conn.compare_configuration()
    print compare_config.tostring

    conn.commit()
    conn.unlock()
    conn.close_session()

if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!', 'candidate')
