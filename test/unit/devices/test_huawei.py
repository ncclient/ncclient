import unittest
from ncclient.devices.huawei import *

capabilities = ['http://www.huawei.com/netconf/capability/execute-cli/1.0',
                'http://www.huawei.com/netconf/capability/action/1.0',
                'http://www.huawei.com/netconf/capability/active/1.0',
                'http://www.huawei.com/netconf/capability/discard-commit/1.0',
                'http://www.huawei.com/netconf/capability/exchange/1.0']

xml1 = '''
<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
  <get>
    <filter type="subtree">
      <acl xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <aclGroups>
          <aclGroup>
            <aclNumOrName>3000</aclNumOrName>
            <aclRuleAdv4s>
              <aclRuleAdv4>
                <aclRuleName>rule_igmp</aclRuleName>
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
    </filter>
  </get>
</rpc>
'''


class TestHuaweiDevice(unittest.TestCase):

    def setUp(self):
        self.obj = HuaweiDeviceHandler({'name': 'huawei'})

    def test_add_additional_operations(self):
        dict = {}
        dict["cli"] = CLI
        dict["action"] = Action
        self.assertEqual(dict, self.obj.add_additional_operations())

    def test_handle_raw_dispatch(self):
        self.assertEqual(xml1, self.obj.handle_raw_dispatch('\0' + xml1 + '\0'))

    def test_get_xml_base_namespace_dict(self):
        self.assertEqual({None: BASE_NS_1_0},
                         self.obj.get_xml_base_namespace_dict())

    def test_get_xml_extra_prefix_kwargs(self):
        d = {}
        d.update(self.obj.get_xml_base_namespace_dict())
        self.assertEqual({"nsmap": d}, self.obj.get_xml_extra_prefix_kwargs())

    def test_get_capabilities(self):
        tcapa = DefaultDeviceHandler().get_capabilities() + capabilities
        self.assertEqual(self.obj.get_capabilities(), tcapa)

    def test_perform_quality_check(self):
        self.assertFalse(self.obj.perform_qualify_check())
