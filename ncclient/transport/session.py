# Copyright 2009 Shikhar Bhushan
# Copyright 2014 Leonidas Poulopoulos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re
import sys
import logging
from threading import Thread, Lock, Event
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty
from ncclient.xml_ import *
from ncclient.capabilities import Capabilities
from ncclient.transport.errors import TransportError, SessionError
from ncclient.transport.notify import Notification

logger = logging.getLogger('ncclient.transport.session')


class Session(Thread):

    "Base class for use by transport protocol implementations."

    def __init__(self, capabilities):
        Thread.__init__(self)
        self.setDaemon(True)
        self._listeners = set()
        self._lock = Lock()
        self.setName('session')
        self._q = Queue()
        self._notification_q = Queue()
        self._client_capabilities = capabilities
        self._server_capabilities = None # yet
        self._id = None # session-id
        self._connected = False # to be set/cleared by subclass implementation
        logger.debug('%r created: client_capabilities=%r' %
                     (self, self._client_capabilities))
        self._device_handler = None # Should be set by child class

    def _dispatch_message(self, raw):
        try:
            root = parse_root(raw)
        except Exception as e:
            device_handled_raw=self._device_handler.handle_raw_dispatch(raw)
            if isinstance(device_handled_raw, str):
                root = parse_root(device_handled_raw)
            elif isinstance(device_handled_raw, Exception):
                self._dispatch_error(device_handled_raw)
                return
            else:
                logger.error('error parsing dispatch message: %s' % e)
                return
        with self._lock:
            listeners = list(self._listeners)
        for l in listeners:
            logger.debug('dispatching message to %r: %s' % (l, raw))
            l.callback(root, raw) # no try-except; fail loudly if you must!

    def _dispatch_error(self, err):
        with self._lock:
            listeners = list(self._listeners)
        for l in listeners:
            logger.debug('dispatching error to %r' % l)
            try: # here we can be more considerate with catching exceptions
                l.errback(err)
            except Exception as e:
                logger.warning('error dispatching to %r: %r' % (l, e))

    def _post_connect(self):
        "Greeting stuff"
        init_event = Event()
        error = [None] # so that err_cb can bind error[0]. just how it is.
        # callbacks
        def ok_cb(id, capabilities):
            self._id = id
            self._server_capabilities = capabilities
            init_event.set()
        def err_cb(err):
            error[0] = err
            init_event.set()
        self.add_listener(NotificationHandler(self._notification_q))
        listener = HelloHandler(ok_cb, err_cb)
        self.add_listener(listener)
        self.send(HelloHandler.build(self._client_capabilities, self._device_handler))
        logger.debug('starting main loop')
        self.start()
        # we expect server's hello message, if server doesn't responds in 60 seconds raise exception
        init_event.wait(60)
        if not init_event.is_set():
            raise SessionError("Capability exchange timed out")
        # received hello message or an error happened
        self.remove_listener(listener)
        if error[0]:
            raise error[0]
        #if ':base:1.0' not in self.server_capabilities:
        #    raise MissingCapabilityError(':base:1.0')
        logger.info('initialized: session-id=%s | server_capabilities=%s' %
                    (self._id, self._server_capabilities))

    def add_listener(self, listener):
        """Register a listener that will be notified of incoming messages and
        errors.

        :type listener: :class:`SessionListener`
        """
        logger.debug('installing listener %r' % listener)
        if not isinstance(listener, SessionListener):
            raise SessionError("Listener must be a SessionListener type")
        with self._lock:
            self._listeners.add(listener)

    def remove_listener(self, listener):
        """Unregister some listener; ignore if the listener was never
        registered.

        :type listener: :class:`SessionListener`
        """
        logger.debug('discarding listener %r' % listener)
        with self._lock:
            self._listeners.discard(listener)

    def get_listener_instance(self, cls):
        """If a listener of the specified type is registered, returns the
        instance.

        :type cls: :class:`SessionListener`
        """
        with self._lock:
            for listener in self._listeners:
                if isinstance(listener, cls):
                    return listener

    def connect(self, *args, **kwds): # subclass implements
        raise NotImplementedError

    def run(self): # subclass implements
        raise NotImplementedError

    def send(self, message):
        """Send the supplied *message* (xml string) to NETCONF server."""
        if not self.connected:
            raise TransportError('Not connected to NETCONF server')
        logger.debug('queueing %s' % message)
        self._q.put(message)

    def scp(self):
        raise NotImplementedError
    ### Properties

    def take_notification(self, block, timeout):
        try:
            return self._notification_q.get(block, timeout)
        except Empty:
            return None

    @property
    def connected(self):
        "Connection status of the session."
        return self._connected

    @property
    def client_capabilities(self):
        "Client's :class:`Capabilities`"
        return self._client_capabilities

    @property
    def server_capabilities(self):
        "Server's :class:`Capabilities`"
        return self._server_capabilities

    @property
    def id(self):
        """A string representing the `session-id`. If the session has not been initialized it will be `None`"""
        return self._id


class SessionListener(object):

    """Base class for :class:`Session` listeners, which are notified when a new
    NETCONF message is received or an error occurs.

    .. note::
        Avoid time-intensive tasks in a callback's context.
    """

    def callback(self, root, raw):
        """Called when a new XML document is received. The *root* argument allows the callback to determine whether it wants to further process the document.

        Here, *root* is a tuple of *(tag, attributes)* where *tag* is the qualified name of the root element and *attributes* is a dictionary of its attributes (also qualified names).

        *raw* will contain the XML document as a string.
        """
        raise NotImplementedError

    def errback(self, ex):
        """Called when an error occurs.

        :type ex: :exc:`Exception`
        """
        raise NotImplementedError


class HelloHandler(SessionListener):

    def __init__(self, init_cb, error_cb):
        self._init_cb = init_cb
        self._error_cb = error_cb

    def callback(self, root, raw):
        tag, attrs = root
        if (tag == qualify("hello")) or (tag == "hello"):
            try:
                id, capabilities = HelloHandler.parse(raw)
            except Exception as e:
                self._error_cb(e)
            else:
                self._init_cb(id, capabilities)

    def errback(self, err):
        self._error_cb(err)

    @staticmethod
    def build(capabilities, device_handler):
        "Given a list of capability URI's returns <hello> message XML string"
        if device_handler:
            # This is used as kwargs dictionary for lxml's Element() function.
            # Therefore the arg-name ("nsmap") is used as key here.
            xml_namespace_kwargs = { "nsmap" : device_handler.get_xml_base_namespace_dict() }
        else:
            xml_namespace_kwargs = {}
        hello = new_ele("hello", **xml_namespace_kwargs)
        caps = sub_ele(hello, "capabilities")
        def fun(uri): sub_ele(caps, "capability").text = uri
        #python3 changes
        if sys.version < '3':
            map(fun, capabilities)
        else:
            list(map(fun, capabilities))
        return to_xml(hello)

    @staticmethod
    def parse(raw):
        "Returns tuple of (session-id (str), capabilities (Capabilities)"
        sid, capabilities = 0, []
        root = to_ele(raw)
        for child in root.getchildren():
            if child.tag == qualify("session-id") or child.tag == "session-id":
                sid = child.text
            elif child.tag == qualify("capabilities") or child.tag == "capabilities" :
                for cap in child.getchildren():
                    if cap.tag == qualify("capability") or cap.tag == "capability":
                        capabilities.append(cap.text)
        return sid, Capabilities(capabilities)


class NotificationHandler(SessionListener):
    def __init__(self, notification_q):
        self._notification_q = notification_q

    def callback(self, root, raw):
        tag, _ = root
        if tag == qualify('notification', NETCONF_NOTIFICATION_NS):
            self._notification_q.put(Notification(raw))

    def errback(self, _):
        pass
