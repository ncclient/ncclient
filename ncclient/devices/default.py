"""
Handler for default device information.

Some devices require very specific information and action during client interaction.

The "device handlers" provide a number of callbacks that return the necessary
information. This allows the ncclient code to merely call upon this device handler -
once configured - instead of cluttering its code with if-statements.

Initially, not much is dealt with by the handler. However, in the future, as more
devices with specific handling are added, more handlers and more functions should be
implememted here, so that the ncclient code can use these callbacks to fill in the
device specific information.

Note that for proper import, the classname has to be:

    "<Devicename>DeviceHandler"

...where <Devicename> is something like "Default", "Nexus", etc.

All device-specific handlers derive from the DefaultDeviceHandler, which implements the
generic information needed for interaction with a Netconf server.

"""
class DefaultDeviceHandler(object):
    """
    Default handler for device specific information.

    """
    def __init__(self, device_params=None):
        self.device_params = device_params

    def get_capabilities(self):
        """
        Return the capability list.

        A list of URI's representing the client's capabilities. This is used during
        the initial capability exchange. Modify (in a new device-handler subclass)
        as needed.

        """
        return [
            "urn:ietf:params:netconf:base:1.0",
            "urn:ietf:params:netconf:capability:writable-running:1.0",
            "urn:ietf:params:netconf:capability:candidate:1.0",
            "urn:ietf:params:netconf:capability:confirmed-commit:1.0",
            "urn:ietf:params:netconf:capability:rollback-on-error:1.0",
            "urn:ietf:params:netconf:capability:startup:1.0",
            "urn:ietf:params:netconf:capability:url:1.0?scheme=http,ftp,file,https,sftp",
            "urn:ietf:params:netconf:capability:validate:1.0",
            "urn:ietf:params:netconf:capability:xpath:1.0",
            "urn:liberouter:params:netconf:capability:power-control:1.0",
            "urn:ietf:params:netconf:capability:interleave:1.0"
        ]

    def get_xml_base_namespace_dict():
        """
        A dictionary containing an "xmlns" element.

        """
        return {}

    def get_xml_extra_prefix_kwargs(self):
        """
        Return any extra prefix that should be sent with each RPC request.

        """
        return {}

    def get_ssh_subsystem_name(self):
        """
        Return the name of the SSH subsystem on the server.

        """
        return "netconf"




