"""
Handler for Cisco CSR device specific information.

Note that for proper import, the classname has to be:

    "<Devicename>DeviceHandler"

...where <Devicename> is something like "Default", "Nexus", etc.

All device-specific handlers derive from the DefaultDeviceHandler, which implements the
generic information needed for interaction with a Netconf server.

"""

from .default import DefaultDeviceHandler
from ncclient.operations.third_party.juniper.rpc import GetConfiguration, LoadConfiguration, CompareConfiguration
from ncclient.operations.third_party.juniper.rpc import ExecuteRpc, Command, Reboot, Halt

class JunosDeviceHandler(DefaultDeviceHandler):
    """
    Juniper handler for device specific information.

    """
    def __init__(self, device_params):
        super(JunosDeviceHandler, self).__init__(device_params)

    def add_additional_operations(self):
        dict = {}
        dict["rpc"] = ExecuteRpc
        dict["get_configuration"] = GetConfiguration
        dict["load_configuration"] = LoadConfiguration
        dict["compare_configuration"] = CompareConfiguration
        dict["command"] = Command
        dict["reboot"] = Reboot
        dict["halt"] = Halt
        return dict

    def perform_qualify_check(self):
        return False
