from .default import DefaultDeviceHandler

class AluDeviceHandler(DefaultDeviceHandler):
    """
    Alcatel-Lucent 7x50 handler for device specific information.
    """
    
    def __init__(self, device_params):
        super(AluDeviceHandler, self).__init__(device_params)

    def get_capabilities(self):
        return [
            "urn:ietf:params:netconf:base:1.0",
        ]
