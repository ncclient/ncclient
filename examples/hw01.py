# -*-coding: UTF-8 -*-
# some code copy from the url:
# https://github.com/HuaweiSwitch/CloudEngine-Ansible/blob/master/module_utils/ce.py

import sys
import re
from ncclient import manager

HW_HOST="192.168.x.x"
HW_PORT=22
HW_USERNAME="admin_xx"
HW_PASSWORD="pass_xx"

req_acl_info = '''
      <acl xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <aclGroups>
          <aclGroup>
            <aclNumOrName>port80_block_acl</aclNumOrName>
            <aclRuleAdv4s>
              <aclRuleAdv4>
                <aclRuleName></aclRuleName>
                <aclRuleID/>
                <aclAction/>
                 <aclActiveStatus/>
                <aclProtocol/>
                <aclSourceIp/>
                <aclSrcWild/>
                <aclDestIp/>
                <aclDestWild/>
                <aclSrcPortOp/>
                <aclSrcPortBegin/>
                <aclSrcPortEnd/>
                <aclDestPortOp/>
                <aclDestPortB/>
                <aclDestPortE/>
                <aclFragType/>
                <aclPrecedence/>
                <aclTos/>
                <aclDscp/>
                <aclIcmpName/>
                <aclIcmpType/>
                <aclIcmpCode/>
                <aclTtlExpired/>
                <vrfName/>
                <aclSynFlag/>
                <aclEstablished/>
                <aclTimeName/>
                <aclRuleDescription/>
                <aclIgmpType/>
              </aclRuleAdv4>
            </aclRuleAdv4s>
          </aclGroup>
        </aclGroups>
      </acl>
'''

_, ip = sys.argv


def get_nc_set_id(xml_str):
    """get netconf set-id value"""

    result = re.findall(r'<rpc-reply.+?set-id=\"(\d+)\"', xml_str)
    if not result:
        return None
    return result[0]


def get_xml_line(xml_list, index):
    """get xml specified line valid string data"""

    ele = None
    while xml_list and not ele:
        if index >= 0 and index >= len(xml_list):
            return None
        if index < 0 and abs(index) > len(xml_list):
            return None

        ele = xml_list[index]
        if not ele.replace(" ", ""):
            xml_list.pop(index)
            ele = None
    return ele


def merge_nc_xml(xml1, xml2):
    """merge xml1 and xml2"""

    xml1_list = xml1.split("</data>")[0].split("\n")
    xml2_list = xml2.split("<data>")[1].split("\n")

    while True:
        xml1_ele1 = get_xml_line(xml1_list, -1)
        xml1_ele2 = get_xml_line(xml1_list, -2)
        xml2_ele1 = get_xml_line(xml2_list, 0)
        xml2_ele2 = get_xml_line(xml2_list, 1)
        if not xml1_ele1 or not xml1_ele2 or not xml2_ele1 or not xml2_ele2:
            return xml1

        if "xmlns" in xml2_ele1:
            xml2_ele1 = xml2_ele1.lstrip().split(" ")[0] + ">"
        if "xmlns" in xml2_ele2:
            xml2_ele2 = xml2_ele2.lstrip().split(" ")[0] + ">"
        if xml1_ele1.replace(" ", "").replace("/", "") == xml2_ele1.replace(" ", "").replace("/", ""):
            if xml1_ele2.replace(" ", "").replace("/", "") == xml2_ele2.replace(" ", "").replace("/", ""):
                xml1_list.pop()
                xml2_list.pop(0)
            else:
                break
        else:
            break

    return "\n".join(xml1_list + xml2_list)

def get_all_config(xml_str, session=None):
    """get-next loop, finally will be getting all config data"""
    set_id = get_nc_set_id(xml_str)
    if not set_id:
        return xml_str
    # continue to get next
    while set_id:
        acl_xml_next = session.get_next(set_id=set_id)
        if "<data/>" in acl_xml_next.xml:
            break
        # merge two xml data
        xml_str = merge_nc_xml(xml_str, acl_xml_next.xml)
        set_id = get_nc_set_id(acl_xml_next.xml)
    return xml_str

netconf = manager.connect(host=HW_HOST,
                          port=HW_PORT,
                          username=HW_USERNAME,
                          password=HW_PASSWORD,
                          hostkey_verify=False,
                          look_for_keys=False,
                          allow_agent=False,
                          device_params={'name': 'huawei'})
acl_data =  netconf.get(('subtree', req_acl_info))
xml_str = get_all_config(acl_data.xml, session=netconf)
print xml_str