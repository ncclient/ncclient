#! /usr/bin/env python
#
# Connect to the NETCONF server passed on the command line using libssh
# and display the client capabilities. For brevity and clarity of the
# examples, we omit proper exception handling.
#
# $ ./nc11.py host username password

import logging
import os
import sys
import warnings

warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager

def demo(host, user, password):
    with manager.connect(
            host=host, port=830,
            username=user, password=password,
            # use_libssh=True,
            hostkey_verify=False) as m:

        for c in m.client_capabilities:
            print(c)

if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
    demo(sys.argv[1], sys.argv[2], sys.argv[3])
