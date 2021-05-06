#! /usr/bin/env python
#
# Connect to the NETCONF server passed on the command line and
# set a device_params to turn on/off the namespace prefix "nc".
# if you want to verify the result, you can print the request that
# was sent. For brevity and clarity of the examples, we omit proper
# exception handling.
#
# $ ./ericsson_nc_prefix_example.py host username password

import sys, os, warnings
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager


def ericsson_connect(host, port, user, password, device_params):
    return manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           device_params=device_params,
                           hostkey_verify-false)


def enable_nc_prefix(host, user, password):
    # add a parameter 'with_ns' to turn on/off 'nc'
    device_params = {'name': 'ericsson', 'with_ns': True}
    with ericsson_connect(host,
                          port=22,
                          user=user,
                          password=password,
                          device_params=device_params) as m:

        ret = m.get_config(source="running").data_xml
        print(ret)


def disable_nc_prefix(host, user, password):
    # add a parameter 'with_ns' to turn on/off 'nc'
    device_params = {'name': 'ericsson', 'with_ns': False}
    with ericsson_connect(host,
                          port=22,
                          user=user,
                          password=password,
                          device_params=device_params) as m:

        ret = m.get_config(source="running").data_xml
        print(ret)


def demo(host, user, password):
    enable_nc_prefix(host, user, password)
    print("#"*50)
    disable_nc_prefix(host, user, password)


if __name__ == '__main__':
    demo(sys.argv[1], sys.argv[2], sys.argv[3])

