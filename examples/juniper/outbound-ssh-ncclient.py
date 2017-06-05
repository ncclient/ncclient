#!/usr/bin/env python

"""
 Listen on TCP port 2200 for incoming SSH session from Junos devices with
 the following ssh outbound configuration and collect host-name and junos-version
 upon connect, then terminate

 lab@router> show configuration system services outbound-ssh
 client outbound-ssh-ncclient {
     device-id vRR;
     services netconf;
     10.0.2.2 port 2200;
  }

 Example:

 $ ./outbound-ssh-ncclient.py
 Listening on port 2200 for incoming sessions ...
 Got a connection from 172.17.0.1:48038!
 MSG DEVICE-CONN-INFO V1 vRR
 Logging in ...
 requesting info...
   Hostname: vRR
    Version: 16.1R3.10
 $
"""


import sys
import socket
import time

from ncclient import manager
from ncclient.xml_ import *


def listener(port, user, password):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    s.listen(5)
    print('Listening on port %d for incoming sessions ...' % (port))
    while True:
        client, addr = s.accept()
        print('Got a connection from %s:%d!' % (addr[0], addr[1]))
        launch_junos_proxy(client, addr, user, password)


def launch_junos_proxy(client, addr, user, password):
    val = {
        'MSG-ID': None,
        'MSG-VER': None,
        'DEVICE-ID': None
    }
    msg = ''
    count = 3
    while len(msg) < 100 and count > 0:
        c = client.recv(1)
        c = c.decode()
        if c == '\r':
            continue

        if c == '\n':
            count -= 1
            if msg.find(':'):
                (key, value) = msg.split(': ')
                val[key] = value
                msg = ''
        else:
            msg += c

    print('MSG %s %s %s' % (val['MSG-ID'], val['MSG-VER'], val['DEVICE-ID']))
    print('Logging in ...')

    sock_fd = client.fileno()
    conn = manager.connect(host=None,
                           sock_fd=sock_fd,
                           username=user,
                           password=password,
                           timeout=10,
                           device_params={'name': 'junos'},
                           hostkey_verify=False)

    rpc = new_ele('get-software-information')

    print('requesting info...')
    result = conn.rpc(rpc)
    print('   Hostname: ' +  result.xpath('//software-information/host-name')[0].text)
    print('    Version: ' + result.xpath('//software-information/junos-version')[0].text)
    sys.exit(0)


if __name__ == '__main__':
    listener(2200, 'netconf', 'juniper!')
