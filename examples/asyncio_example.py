#! /usr/bin/env python
#
# Connect to the NETCONF server passed on the command line, and
# setting async mode ensures that the RPC.request() only sends
# the request and does not wait synchronously for a response.
# This script and the following scripts all assume that the user
# calling the script is known by the server and that suitable
# SSH keys are in place. For brevity and clarity of example,
# we omit proper exception handling.
#
# $ ./asyncio_example.py host user password

from ncclient import manager
import logging, asyncio, sys

filter1 = '''
    <top xmlns="xxx.org">
      <name/>
    </top>
    '''

filter2 = '''
    <top xmlns="xxx.org">
      <host/>
    </top>
    '''

filter3 = '''<top xmlns="xxx.org"/>'''

def connect(host, user, password):
    return manager.connect(
        host=host,
        port=22,
        username=user,
        password=password,
        device_params={'name': 'junos'},
        async_mode=True,
        timeout=10,
        hostkey_verify=False)


async def multi_operations(loop, conn):
    # the requests to be sent by the client 
    req = [
        conn.get_config(source='running', filter=('subtree', filter1)),
        conn.get(filter=('subtree', filter2)),
        conn.get_config(source='running', filter=('subtree', filter3)),
        conn.lock(target='running'),
        conn.lock(target='running'),
        ]

    # add asynchronously all requests to asyncio.BaseEventloop
    tasks = [loop.create_task(r) for r in req]
    # waiting for all responses from the server
    dones = await asyncio.gather(*tasks)
    for i in dones:
        print("result: %s" % i)
 
def demo(host, user, password):
    conn = connect(host, user, password)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(multi_operations(loop, conn))
    loop.close()

if __name__ == "__main__":
    demo(sys.argv[1], sys.argv[2], sys.argv[3])
