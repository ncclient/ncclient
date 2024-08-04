#! /usr/bin/env python
#
# Connect to NETCONF server using unix socket passed on the command line.
# Then display the servers capabilities. After connecting you can also use 
# all other operations supported by ncclient, example: get(), get_config()...
#
# To test against a example NETCONF server with unix socket support check out:
# https://github.com/CESNET/libnetconf2
# It contains an example server which can listen for connections using a unix 
# socket.
#
# $ ./nc10.py "/path/to/socket"

import sys, warnings
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager

def demo(path):
    with manager.connect_uds(path) as m:
        for c in m.server_capabilities:
            print(c)

if __name__ == '__main__':
    demo(sys.argv[1])