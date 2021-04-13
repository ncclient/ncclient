# Copyright 2009 Shikhar Bhushan
# Copyright 2011 Leonidas Poulopoulos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module is a thin layer of abstraction around the library.
It exposes all core functionality.
"""

from ncclient.sync_manager import Manager
from ncclient import transport
import socket
import logging
import sys

if sys.version_info.major > 2:
    from asyncio import *
    from ncclient.async_manager import asyncio_connect

logger = logging.getLogger('ncclient.manager')

def make_device_handler(device_params):
    """
    Create a device handler object that provides device specific parameters and
    functions, which are called in various places throughout our code.

    If no device_params are defined or the "name" in the parameter dict is not
    known then a default handler will be returned.

    """
    if device_params is None:
        device_params = {}

    handler = device_params.get('handler', None)
    if handler:
        return handler(device_params)

    device_name = device_params.get("name", "default")
    # Attempt to import device handler class. All device handlers are
    # in a module called "ncclient.devices.<devicename>" and in a class named
    # "<devicename>DeviceHandler", with the first letter capitalized.
    class_name          = "%sDeviceHandler" % device_name.capitalize()
    devices_module_name = "ncclient.devices.%s" % device_name
    dev_module_obj      = __import__(devices_module_name)
    handler_module_obj  = getattr(getattr(dev_module_obj, "devices"), device_name)
    class_obj           = getattr(handler_module_obj, class_name)
    handler_obj         = class_obj(device_params)
    return handler_obj


def _extract_device_params(kwds):
    device_params = kwds.pop("device_params", None)

    return device_params

def _extract_manager_params(kwds):
    manager_params = kwds.pop("manager_params", {})

    # To maintain backward compatibility
    if 'timeout' not in manager_params and 'timeout' in kwds:
        manager_params['timeout'] = kwds['timeout']
    return manager_params


def connect_ssh(*args, **kwds):
    """
    Initialize a :class:`Manager` over the SSH transport.
    For documentation of arguments see :meth:`ncclient.transport.SSHSession.connect`.

    The underlying :class:`ncclient.transport.SSHSession` is created with
    :data:`CAPABILITIES`. It is first instructed to
    :meth:`~ncclient.transport.SSHSession.load_known_hosts` and then
    all the provided arguments are passed directly to its implementation
    of :meth:`~ncclient.transport.SSHSession.connect`.

    To customize the :class:`Manager`, add a `manager_params` dictionary in connection
    parameters (e.g. `manager_params={'timeout': 60}` for a bigger RPC timeout parameter)

    To invoke advanced vendor related operation add
    `device_params={'name': '<vendor_alias>'}` in connection parameters. For the time,
    'junos' and 'nexus' are supported for Juniper and Cisco Nexus respectively.

    A custom device handler can be provided with
    `device_params={'handler':<handler class>}` in connection parameters.
    """
    # Extract device parameter and manager parameter dictionaries, if they were passed into this function.
    # Remove them from kwds (which should keep only session.connect() parameters).
    device_params = _extract_device_params(kwds)
    manager_params = _extract_manager_params(kwds)

    device_handler = make_device_handler(device_params)
    device_handler.add_additional_ssh_connect_params(kwds)
    session = transport.SSHSession(device_handler)
    if "hostkey_verify" not in kwds or kwds["hostkey_verify"]:
        session.load_known_hosts()

    try:
       session.connect(*args, **kwds)
    except Exception as ex:
        if session.transport:
            session.close()
        raise
    return Manager(session, device_handler, **manager_params)

def connect_ioproc(*args, **kwds):
    device_params = _extract_device_params(kwds)
    manager_params = _extract_manager_params(kwds)

    if device_params:
        import_string = 'ncclient.transport.third_party.'
        import_string += device_params['name'] + '.ioproc'
        third_party_import = __import__(import_string, fromlist=['IOProc'])

    device_handler = make_device_handler(device_params)

    session = third_party_import.IOProc(device_handler)
    session.connect()

    return Manager(session, device_handler, **manager_params)

def connect(*args, **kwds):
    # use sync_mode by default
    mode = kwds.pop("async_mode", False)
    if mode is True and sys.version_info.major > 2:
        return async_connect(*args, **kwds)
    else:
        return sync_connect(*args, **kwds)

def async_connect(*args, **kwds):
    loop = get_event_loop()
    task = loop.create_task(asyncio_connect(loop=loop, handler=sync_connect, *args, **kwds))
    try:
        return loop.run_until_complete(task)
    except Exception as e:
        loop.close()
        raise

def sync_connect(*args, **kwds):
    if "host" in kwds:
        host = kwds["host"]
        device_params = kwds.get('device_params', {})
        if host == 'localhost' and device_params.get('name') == 'junos' \
                and device_params.get('local'):
            return connect_ioproc(*args, **kwds)
        else:
            return connect_ssh(*args, **kwds)

def call_home(*args, **kwds):
    host = kwds["host"]
    port = kwds.get("port",4334)
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.bind((host, port))
    srv_socket.settimeout(10)
    srv_socket.listen()
    
    sock, remote_host = srv_socket.accept()
    logger.info('Callhome connection initiated from remote host {0}'.format(remote_host))
    kwds['sock'] = sock
    return connect_ssh(*args, **kwds)

