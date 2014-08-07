# python

from ncclient import manager
from ncclient.xml_ import *

from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises


class Test_NCElement(object):

    def test_ncelement_reply_001(self):
        """test parse rpc_reply and string/data_xml"""
        #read in reply1 contents
        with open('test/reply1', 'r') as f:
            reply = f.read()
        device_params = {'name':'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(reply, transform_reply)
        assert_equal(str(result), result.tostring)
        #data_xml != tostring
        assert_not_equal(result.tostring, result.data_xml)

    def test_ncelement_reply_002(self):
        """test parse rpc_reply and xpath"""
        #read in reply1 contents
        with open('test/reply1', 'r') as f:
            reply = f.read()
        device_params = {'name':'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(reply, transform_reply)
        #XPATH checks work
        assert_equal(result.xpath("//host-name")[0].text,"R1")
        assert_equal(result.xpath("/rpc-reply/software-information/host-name")[0].text,"R1")
        assert_equal(result.xpath("software-information/host-name")[0].text,"R1")

    def test_ncelement_reply_003(self):
        """test parse rpc_reply and find"""
        #read in reply1 contents
        with open('test/reply1', 'r') as f:
            reply = f.read()
        device_params = {'name':'junos'}
        device_handler = manager.make_device_handler(device_params)
        transform_reply = device_handler.transform_reply()
        result = NCElement(reply, transform_reply)
        #find
        assert_equal(result.findtext(".//host-name"),"R1")
        assert_equal(result.find(".//host-name").tag,"host-name")
