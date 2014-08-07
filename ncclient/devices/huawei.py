"""
Handler for Huawei device specific information.

Note that for proper import, the classname has to be:

    "<Devicename>DeviceHandler"

...where <Devicename> is something like "Default", "Huawei", etc.

All device-specific handlers derive from the DefaultDeviceHandler, which implements the
generic information needed for interaction with a Netconf server.

"""

from ncclient.xml_ import BASE_NS_1_0
from lxml import etree
import re

from .default import DefaultDeviceHandler

class HuaweiDeviceHandler(DefaultDeviceHandler):
    """
    Huawei handler for device specific information.

    In the device_params dictionary, which is passed to __init__, you can specify
    the parameter "ssh_subsystem_name". That allows you to configure the preferred
    SSH subsystem name that should be tried on your Huawei switch. If connecting with
    that name fails, or you didn't specify that name, the other known subsystem names
    will be tried. However, if you specify it then this name will be tried first.

    """
    _EXEMPT_ERRORS = []

    def __init__(self, device_params):
        super(HuaweiDeviceHandler, self).__init__(device_params)

    def get_capabilities(self):
        # Just need to replace a single value in the default capabilities
        c = super(HuaweiDeviceHandler, self).get_capabilities()
        return c

    def get_xml_base_namespace_dict(self):
        return { "xmlns":BASE_NS_1_0 }

    def get_xml_extra_prefix_kwargs(self):
        d = {
                # "xmlns":"http://www.huawei.com/netconf/vrp"
            }
        d.update(self.get_xml_base_namespace_dict())
        return d

    def get_xml_app_namespace_dict(self):
        return { "xmlns":"http://www.huawei.com/netconf/vrp",
                 "content-version": "1.0",
                 "format-version": "1.0"}

    def get_applications_name(self, type):

        application = {
            "vlan":"vlan",
            "interface":"ifm",
            "ethernet":"ethernet"
        }
        return application.get(type)

    def get_vlan_id_filter(self,vlan_id):
        snippet = """
<vlan xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
    <vlans>
        <vlan>
            <vlanId>%s</vlanId>
            <vlanName/>
            <vlanDesc/>
        </vlan>
    </vlans>
</vlan>"""
        filter_content = snippet % (vlan_id)
        return filter_content

    def get_vlan_name_filter(self,vlan_name):
        snippet = """
<vlan xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
    <vlans>
        <vlan>
            <vlanId/>
            <vlanName/>
            <vlanDesc>%s</vlanDesc>
        </vlan>
    </vlans>
</vlan>"""
        filter_content = snippet % (vlan_name)
        return filter_content

    def parse_vlan_id(self,xml):
        root = etree.fromstring(str(xml))
        result = re.match('\{[^\}]*\}', root.tag)
        ns = result.group(0)
        vlan_root = root.find("./%sdata/*" % ns )
        result = re.match('\{[^\}]*\}', vlan_root.tag)
        vlan_ns = result.group(0)
        vlan_list = vlan_root.findall("./%svlans/*" % vlan_ns)
        for vlan in vlan_list:
            vlan_id = vlan.find("./%svlanId" % vlan_ns).text
        if vlan_id:
            return vlan_id

    def parse_vlan_name(self,xml):
        root = etree.fromstring(str(xml))
        result = re.match('\{[^\}]*\}', root.tag)
        ns = result.group(0)
        vlan_root = root.find("./%sdata/*" % ns )
        result = re.match('\{[^\}]*\}', vlan_root.tag)
        vlan_ns = result.group(0)
        vlan_list = vlan_root.findall("./%svlans/*" % vlan_ns)
        for vlan in vlan_list:
            vlan_name = vlan.find("./%svlanDesc" % vlan_ns).text
        if vlan_name:
            return vlan_name
