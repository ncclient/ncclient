#!/usr/bin/env python
#

import logging
import sys

from ncclient import manager
from ncclient.xml_ import to_xml
from ncclient.operations.rpc import RPCError

_NS_MAP = {
    'nc': 'urn:ietf:params:xml:ns:netconf:base:1.0',
    'nokia-conf': 'urn:nokia.com:sros:ns:yang:sr:conf'
}

_NOKIA_MGMT_INT_FILTER = '''
<configure xmlns="%s">
  <system>
    <management-interface/>
  </system>
</configure>
''' % (_NS_MAP['nokia-conf'])

def connect(host, port, user, password):
    m = manager.connect(host=host, port=port,
            username=user, password=password,
            device_params={'name': 'sros'},
            hostkey_verify=False)

    ## Retrieve full configuration from the running datastore
    running_xml = m.get_config(source='running')
    logging.info(running_xml)

    ## Retrieve full configuration from the running datastore and strip
    ## the rpc-reply + data elements
    running_xml = m.get_config(source='running').xpath(
            '/nc:rpc-reply/nc:data/nokia-conf:configure',
            namespaces=_NS_MAP)[0]
    logging.info(to_xml(running_xml, pretty_print=True))

    ## Retrieve full configuration from the running datastore and strip
    ## out elements except for /configure/system/management-interface
    running_xml = m.get_config(source='running').xpath(
            '/nc:rpc-reply/nc:data/nokia-conf:configure' \
            '/nokia-conf:system/nokia-conf:management-interface',
            namespaces=_NS_MAP)[0]
    logging.info(to_xml(running_xml, pretty_print=True))

    ## Retrieve a specific filtered subtree from the running datastore
    ## and handle any rpc-error should a portion of the filter criteria
    ## be invalid
    try:
        running_xml = m.get_config(source='running',
                filter=('subtree', _NOKIA_MGMT_INT_FILTER),
                with_defaults='report-all').xpath(
                        '/nc:rpc-reply/nc:data/nokia-conf:configure',
                        namespaces=_NS_MAP)[0]
        logging.info(to_xml(running_xml, pretty_print=True))

    except RPCError as err:
        logging.info('Error: %s' % err.message.strip())

    m.close_session()

if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    try:
        connect(sys.argv[1], '830', 'admin', 'admin')

    except IndexError:
        logging.error('Must supply a valid hostname or IP address')

