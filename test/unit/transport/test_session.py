import unittest
try:
    from unittest.mock import patch  # Python 3.4 and later
except ImportError:
    from mock import patch
from ncclient.transport.session import *
from ncclient.devices.junos import JunosDeviceHandler
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty
import logging



rpc_reply = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/12.1X46/junos" attrib1 = "test">
    <software-information>
        <host-name>R1</host-name>
        <product-model>firefly-perimeter</product-model>
        <product-name>firefly-perimeter</product-name>
        <package-information>
            <name>junos</name>
            <comment>JUNOS Software Release [12.1X46-D10.2]</comment>
        </package-information>
    </software-information>
    <cli>
        <banner></banner>
    </cli>
</rpc-reply>
"""

hello_rpc_reply = """<hello>
<capabilities>
<capability>candidate</capability>
<capability>validate</capability>
</capabilities>
<session-id>s001</session-id>
</hello>
"""

notification="""
   <notification
      xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
      <eventTime>2007-07-08T00:01:00Z</eventTime>
      <event xmlns="http://example.com/event/1.0">
         <eventClass>fault</eventClass>
         <reportingEntity>
             <card>Ethernet0</card>
         </reportingEntity>
         <severity>major</severity>
       </event>
   </notification>
"""

class TestSession(unittest.TestCase):

    @patch('ncclient.transport.session.HelloHandler.callback')
    def test_dispatch_message(self, mock_handler):
        cap = [':candidate']
        obj = Session(cap)
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj._device_handler = device_handler
        listener = HelloHandler(None, None)
        obj._listeners.add(listener)
        obj._dispatch_message(rpc_reply)
        mock_handler.assert_called_once_with(parse_root(rpc_reply), rpc_reply)

    @patch('ncclient.transport.session.parse_root')
    @patch('ncclient.logging_.SessionLoggerAdapter.error')
    def test_dispatch_message_error(self, mock_log, mock_parse_root):
        mock_parse_root.side_effect = Exception
        cap = [':candidate']
        obj = Session(cap)
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj._device_handler = device_handler
        listener = HelloHandler(None, None)
        obj._listeners.add(listener)
        obj._dispatch_message(rpc_reply)
        self.assertNotEqual(
            mock_log.call_args_list[0][0][0].find("error parsing dispatch message"), -1)

    @patch('ncclient.transport.session.parse_root')
    @patch('ncclient.devices.junos.JunosDeviceHandler.handle_raw_dispatch')
    @patch('ncclient.transport.session.HelloHandler.errback')
    @patch('ncclient.logging_.SessionLoggerAdapter.debug')
    def test_dispatch_message_error2(self, mock_log, mock_errback,
                                     mock_handle_raw_dispatch, mock_parse_root):
        mock_parse_root.side_effect = Exception
        mock_handle_raw_dispatch.return_value = Exception()
        mock_errback.side_effect = Exception
        cap = [':candidate']
        obj = Session(cap)
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj._device_handler = device_handler
        listener = HelloHandler(None, None)
        obj._listeners.add(listener)
        obj._dispatch_message(rpc_reply)
        mock_handle_raw_dispatch.assert_called_once_with(rpc_reply)
        self.assertEqual(
            mock_log.call_args_list[0][0][0].find("error dispatching to"), -1)

    @patch('ncclient.transport.session.HelloHandler.errback')
    def test_dispatch_error(self, mock_handler):
        cap = [':candidate']
        obj = Session(cap)
        listener = HelloHandler(None, None)
        obj._listeners.add(listener)
        obj._dispatch_error("Error")
        mock_handler.assert_called_once_with("Error")

    @patch('ncclient.logging_.SessionLoggerAdapter.info')
    @patch('ncclient.transport.session.Thread.start')
    @patch('ncclient.transport.session.Event')
    def test_post_connect(self, mock_lock, mock_handler, mock_log):
        cap = [':candidate']
        obj = Session(cap)
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj._device_handler = device_handler
        obj._connected = True
        obj._id = 100
        obj._server_capabilities = cap
        obj._post_connect()
        log_args = mock_log.call_args_list[0][0]
        self.assertNotEqual(log_args[0].find("initialized"), -1)
        self.assertNotEqual(log_args[0].find("session-id="), -1)
        self.assertEqual(log_args[1], 100)
        self.assertNotEqual(
            log_args[0].find("server_capabilities="), -1)
        self.assertEqual(log_args[2], [':candidate'])

    @patch('ncclient.logging_.SessionLoggerAdapter.info')
    @patch('ncclient.transport.session.Thread.start')
    @patch('ncclient.transport.session.Event')
    def test_post_connect2(self, mock_lock, mock_handler, mock_log):
        cap = ['urn:ietf:params:netconf:base:1.1']
        obj = Session(cap)
        device_handler = JunosDeviceHandler({'name': 'junos'})
        obj._device_handler = device_handler
        obj._connected = True
        obj._id = 100
        obj._server_capabilities = cap
        obj._post_connect()
        log_args = mock_log.call_args_list[0][0]
        self.assertNotEqual(log_args[0].find("initialized"), -1)
        self.assertNotEqual(log_args[0].find("session-id="), -1)
        self.assertEqual(log_args[1], 100)
        self.assertNotEqual(
            log_args[0].find("server_capabilities="), -1)
        self.assertEqual(log_args[2], ['urn:ietf:params:netconf:base:1.1'])

    def test_add_listener(self):
        cap = [':candidate']
        obj = Session(cap)
        listener = HelloHandler(None, None)
        obj.add_listener(listener)
        self.assertTrue(listener in obj._listeners)

    def test_add_listener_exception(self):
        cap = [':candidate']
        obj = Session(cap)
        listener = Session(None)
        self.assertRaises(SessionError,
            obj.add_listener, listener)

    def test_remove_listener(self):
        cap = [':candidate']
        obj = Session(cap)
        listener = HelloHandler(None, None)
        obj._listeners.add(listener)
        obj.remove_listener(listener)
        self.assertEqual(len(obj._listeners), 0)

    def test_get_listener_instance(self):
        cap = [':candidate']
        obj = Session(cap)
        listener = HelloHandler(None, None)
        obj._listeners.add(listener)
        ret = obj.get_listener_instance(HelloHandler)
        self.assertEqual(ret, listener)

    def test_send_connected(self):
        cap = [':candidate']
        obj = Session(cap)
        obj._connected = True
        obj.send("Hello World")
        self.assertEqual("Hello World", obj._q.get())

    def test_send_disconnected(self):
        cap = [':candidate']
        obj = Session(cap)
        obj._connected = False
        self.assertRaises(TransportError,
            obj.send, "Hello World")

    def test_connected(self):
        cap = [':candidate']
        obj = Session(cap)
        obj._connected = True
        self.assertTrue(obj.connected)

    def test_client_capability(self):
        cap = [':validate']
        obj = Session(cap)
        self.assertEqual(obj.client_capabilities, cap)

    def test_server_capability(self):
        cap = [':validate']
        obj = Session(cap)
        obj._server_capabilities = cap
        self.assertEqual(obj.server_capabilities, cap)

    def test_id(self):
        cap = [':validate']
        obj = Session(cap)
        obj._id = "1000"
        self.assertEqual(obj.id, "1000")

    def test_hello_handler_callback_ok(self):

        def ok_cb(id, capabilities):
            self._id = id
            self._server_capabilities = capabilities

        def err_cb(err):
            self.error = err

        listener = HelloHandler(ok_cb, err_cb)
        listener.callback(parse_root(hello_rpc_reply), hello_rpc_reply)
        caps = ["candidate", "validate"]
        self.assertEqual(self._id, "s001")
        self.assertEqual(
            self._server_capabilities._dict,
            Capabilities(caps)._dict)

    @patch('ncclient.transport.session.HelloHandler.parse')
    def test_hello_handler_callback_error(self, mock_parse):

        def ok_cb(id, capabilities):
            self._id = id
            self._server_capabilities = capabilities

        def err_cb(err):
            self.error = "Error"

        mock_parse.side_effect = Exception
        listener = HelloHandler(ok_cb, err_cb)
        listener.callback(parse_root(hello_rpc_reply), hello_rpc_reply)
        self.assertEqual(self.error, "Error")

    def test_hello_handler_build(self):
        cap = [':candidate', ':validate']
        listener = HelloHandler(None, None)
        result = listener.build(cap, None)
        node = new_ele("hello")
        caps = sub_ele(node, "capabilities")
        sub_ele(caps, "capability").text = ":candidate"
        sub_ele(caps, "capability").text = ":validate"
        node = to_xml(node)
        self.assertEqual(node, result)

    def test_hello_handler_parse(self):
        cap = [':candidate']
        obj = Session(cap)
        listener = HelloHandler(None, None)
        obj._listeners.add(listener)
        id, capabilities = listener.parse(hello_rpc_reply)
        self.assertEqual(id, "s001")
        caps = ["candidate", "validate"]
        self.assertEqual(capabilities._dict, Capabilities(caps)._dict)

    def test_notification_handler_valid_notification(self):
        q = Queue()
        listener = NotificationHandler(q)
        listener.callback(parse_root(notification), notification)
        notif = q.get_nowait()
        self.assertEqual(notif.notification_xml, notification)
        self.assertRaises(Empty, q.get_nowait)

    def test_notification_handler_non_notification(self):
        q = Queue()
        listener = NotificationHandler(q)
        # This handler should ignore things that aren't notifications
        listener.callback(parse_root(rpc_reply), rpc_reply)
        self.assertRaises(Empty, q.get_nowait)

    def test_take_notification(self):
        cap = [':candidate']
        obj = Session(cap)
        obj._notification_q.put('Test object')
        self.assertEqual(obj.take_notification(block=False, timeout=None),
                         'Test object')
        self.assertEqual(obj.take_notification(block=False, timeout=None),
                         None)
