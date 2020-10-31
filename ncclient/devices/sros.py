from lxml import etree

from .default import DefaultDeviceHandler
from ncclient.operations.third_party.sros.rpc import MdCliRawCommand
from ncclient.xml_ import BASE_NS_1_0


def passthrough(xml):
    return xml

class SrosDeviceHandler(DefaultDeviceHandler):
    """
    Nokia SR OS handler for device specific information.
    """

    def __init__(self, device_params):
        super(SrosDeviceHandler, self).__init__(device_params)

    def get_capabilities(self):
        return [
            'urn:ietf:params:netconf:base:1.0',
            'urn:ietf:params:netconf:base:1.1',
            'urn:ietf:params:netconf:capability:candidate:1.0',
            'urn:ietf:params:netconf:capability:confirmed-commit:1.1',
            'urn:ietf:params:netconf:capability:rollback-on-error:1.0',
            'urn:ietf:params:netconf:capability:notification:1.0',
            'urn:ietf:params:netconf:capability:interleave:1.0',
            'urn:ietf:params:netconf:capability:validate:1.0',
            'urn:ietf:params:netconf:capability:validate:1.1',
            'urn:ietf:params:netconf:capability:startup:1.0',
            'urn:ietf:params:netconf:capability:url:1.0?scheme=ftp,tftp,file',
            'urn:ietf:params:netconf:capability:with-defaults:1.0?basic-mode=explicit&amp;also-supported=report-all',
            'urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring']

    def get_xml_base_namespace_dict(self):
        return {None: BASE_NS_1_0}

    def get_xml_extra_prefix_kwargs(self):
        d = {}
        d.update(self.get_xml_base_namespace_dict())
        return {"nsmap": d}

    def add_additional_operations(self):
        operations = {
            'md_cli_raw_command': MdCliRawCommand
        }
        return operations

    def perform_qualify_check(self):
        return False

    def transform_reply(self):
        return passthrough
