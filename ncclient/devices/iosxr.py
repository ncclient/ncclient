"""
Handler for Cisco IOS-XR device specific information.

Note that for proper import, the classname has to be:

    "<Devicename>DeviceHandler"

...where <Devicename> is something like "Default", "Nexus", etc.

All device-specific handlers derive from the DefaultDeviceHandler, which implements the
generic information needed for interaction with a Netconf server.

"""


from .default import DefaultDeviceHandler
from ncclient.operations.third_party.iosxr.rpc import ExecuteRpc

def iosxr_unknown_host_cb(host, fingerprint):
        #This will ignore the unknown host check when connecting to IOS-XR devices
        return True

class IosxrDeviceHandler(DefaultDeviceHandler):
    """
    Cisco IOS-XR handler for device specific information.

    """
    def __init__(self, device_params):
        super(IosxrDeviceHandler, self).__init__(device_params)

    def add_additional_ssh_connect_params(self, kwargs):
        kwargs['allow_agent']   = False
        kwargs['look_for_keys'] = False
        kwargs['hostkey_verify'] = False
        kwargs['unknown_host_cb'] = iosxr_unknown_host_cb

    def perform_qualify_check(self):
        return False

    def add_additional_operations(self):
        dict = {}
        dict["rpc"] = ExecuteRpc
        # dict["get_configuration"] = GetConfiguration
        # dict["command"] = Command
        # dict["commit"] = Commit
        return dict
    
