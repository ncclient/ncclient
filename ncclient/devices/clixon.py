"""
Handler for Clixon based device specific information.

Note that for proper import, the classname has to be:

    "<Devicename>DeviceHandler"

...where <Devicename> is something like "Default", "Nexus", etc.

All device-specific handlers derive from the DefaultDeviceHandler, which implements the
generic information needed for interaction with a Netconf server.

"""


from .default import DefaultDeviceHandler

def iosxr_unknown_host_cb(host, fingerprint):
        #This will ignore the unknown host check when connecting to Clixon based devices
        return True

class ClixonDeviceHandler(DefaultDeviceHandler):
    """
    Clixon handler for device specific information.

    """
    def __init__(self, device_params):
        super(ClixonDeviceHandler, self).__init__(device_params)

    def perform_qualify_check(self):
        return False
