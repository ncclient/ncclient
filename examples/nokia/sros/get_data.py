#!/usr/bin/env python
#

import logging
import sys

from ncclient import manager

from ncclient._types import Datastore
from ncclient._types import FilterType
from ncclient._types import WithDefaults
from ncclient._types import Origin

from ncclient.namespaces import IETF
from ncclient.namespaces import Nokia

from ncclient.xml_ import to_xml
from ncclient.operations.rpc import RPCError

_NS_MAP = IETF.nsmap
_NS_MAP.update(Nokia.nsmap)

_NOKIA_CONF_MGMT_INT_FILTER = '''
<configure xmlns="%s">
  <system>
    <management-interface/>
  </system>
</configure>
''' % (_NS_MAP['conf'])


def connect(host, port, user, password):
    m = manager.connect(host=host, port=port,
            username=user, password=password,
            device_params={'name': 'sros'},
            hostkey_verify=False)

    ## Issue get-data on the candidate datastore with a subtree filter,
    ## with-defaults and a max-depth of '3' and display the raw XML
    ## output
    try:
        result = m.get_data(datastore=Datastore.CANDIDATE,
                filter=(FilterType.SUBTREE, _NOKIA_CONF_MGMT_INT_FILTER),
                max_depth=3, with_defaults=WithDefaults.REPORT_ALL)
        logging.info(result)

    except RPCError as err:
        logging.error(err)

    ## Issue get-data on the intended datastore with a subtree filter,
    ## with-defaults and display the raw XML output
    try:
        result = m.get_data(datastore=Datastore.INTENDED,
                filter=(FilterType.SUBTREE, _NOKIA_CONF_MGMT_INT_FILTER),
                with_defaults=WithDefaults.REPORT_ALL)
        logging.info(result)

    except RPCError as err:
        logging.error(err)


    m.close_session()

if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    try:
        connect(sys.argv[1], '830', 'admin', 'admin')

    except IndexError:
        logging.error('Must supply a valid hostname or IP address')

