"""
Handler for Cisco Nexus device specific information.

Note that for proper import, the classname has to be:

    "<Devicename>DeviceHandler"

...where <Devicename> is something like "Default", "Nexus", etc.

All device-specific handlers derive from the DefaultDeviceHandler, which implements the
generic information needed for interaction with a Netconf server.

"""

from ncclient.xml_ import BASE_NS_1_0

from .default import DefaultDeviceHandler

class NexusDeviceHandler(DefaultDeviceHandler):
    """
    Cisco Nexus handler for device specific information.

    """
    _EXEMPT_ERRORS = [
        "*VLAN with the same name exists*", # returned even if VLAN was created, but
                                            # name was already in use (switch will
                                            # automatically choose different, unique
                                            # name for VLAN)
    ]

    def __init__(self, device_params):
        super(NexusDeviceHandler, self).__init__(device_params)

    def get_capabilities(self):
        # Just need to replace a single value in the default capabilities
        c = super(NexusDeviceHandler, self).get_capabilities()
        c[0] = "urn:ietf:params:xml:ns:netconf:base:1.0"
        return c

    def get_xml_base_namespace_dict(self):
        return { "xmlns":BASE_NS_1_0 }

    def get_xml_extra_prefix_kwargs(self):
        d = {
                "xmlns:nxos":"http://www.cisco.com/nxos:1.0",
                "xmlns:if":"http://www.cisco.com/nxos:1.0:if_manager"
            }
        d.update(self.get_xml_base_namespace_dict())
        return d

    def get_ssh_subsystem_name(self):
        return "xmlagent"

