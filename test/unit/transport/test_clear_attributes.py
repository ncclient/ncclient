from ncclient import manager
from ncclient import transport
from ncclient.manager import Manager

import re

import os

from mock import Mock
from mock import create_autospec

from nose.tools import assert_equal

from unittest import TestCase

class Test_LXML_problem(TestCase):

    def test_clear_attributes_from_previous_message(self):
        """test sending multiple messages results in valid xml"""

        test_dir = os.path.dirname(os.path.realpath(__file__))

        # setup ncclient
        device_handler = manager.make_device_handler({'name':'nexus'})
        session = transport.Session(device_handler)
        def mock_send(self, message='Not Set'):
            pass
        mock_send_function = create_autospec(mock_send, return_value="<test/>")
        session.send = Mock(side_effect=mock_send_function)
        session._connected = True
        mgr = Manager(session, device_handler)
        mgr._async_mode = True

        # make first get call
        mgr.get(filter=('subtree', '<cmd>show version</cmd>'))
        xml_string = mock_send_function.mock_calls[0][1][0] # first call, second arg, value
        xml_string = self._normalize_uuid(xml_string)
        assert_equal(self._read_test_string(test_dir + '/expected_get_message.xml'), xml_string)
        mock_send_function.reset_mock()

        # make an edit-config call
        config = '''<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <configure>
                        <__XML__MODE__exec_configure>
                          <vlan>
                            <vlan-id-create-delete>
                              <__XML__PARAM_value>1</__XML__PARAM_value>
                                <__XML__MODE_vlan>
                                  <name>
                                    <vlan-name>1</vlan-name>
                                  </name>
                                </__XML__MODE_vlan>
                              </vlan-id-create-delete>
                            </vlan>
                        </__XML__MODE__exec_configure>
                      </configure>
                    </config>'''
        config = ' '.join(config.split())


        mgr.edit_config(target='running', config=config)
        xml_string = mock_send_function.mock_calls[0][1][0]
        xml_string = self._normalize_uuid(xml_string)
        # using lxml 3.2.1 attributes from the get message bleed into the edit
        assert_equal(self._read_test_string(test_dir + '/expected_edit_message.xml'), xml_string)

    def _normalize_uuid(self, x):
        """replace the UUID, so we can compare apples to apples"""
        return re.sub(r"urn:uuid:[a-z0-9\-]*", "urn:uuid:UUID-HERE", x)


    def _read_test_string(self, file):
        with open(file, 'r') as f:
            text = f.read()
        return text
