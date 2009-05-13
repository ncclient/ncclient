# Copyright 2009 Shikhar Bhushan
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

from Queue import Queue
from threading import Thread, Lock, Event

from ncclient import content
from ncclient.capabilities import Capabilities

import logging
logger = logging.getLogger('ncclient.transport.session')

class Session(Thread):
    
    def __init__(self, capabilities):
        Thread.__init__(self)
        self.set_daemon(True)
        self._listeners = set() # 3.0's weakset ideal
        self._lock = Lock()
        self.set_name('session')
        self._q = Queue()
        self._client_capabilities = capabilities
        self._server_capabilities = None # yet
        self._id = None # session-id
        self._connected = False # to be set/cleared by subclass implementation
        logger.debug('%r created: client_capabilities=%r' %
                     (self, self._client_capabilities))
    
    def _dispatch_message(self, raw):
        "TODO: docstring"
        try:
            root = content.parse_root(raw)
        except Exception as e:
            logger.error('error parsing dispatch message: %s' % e)
            return
        with self._lock:
            listeners = list(self._listeners)
        for l in listeners:
            logger.debug('dispatching message to %r' % l)
            try:
                l.callback(root, raw)
            except Exception as e:
                logger.warning('[error] %r' % e)
    
    def _dispatch_error(self, err):
        "TODO: docstring"
        with self._lock:
            listeners = list(self._listeners)
        for l in listeners:
            logger.debug('dispatching error to %r' % l)
            try:
                l.errback(err)
            except Exception as e:
                logger.warning('error %r' % e)
    
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
        listener = HelloHandler(ok_cb, err_cb)
        self.add_listener(listener)
        self.send(HelloHandler.build(self._client_capabilities))
        logger.debug('starting main loop')
        self.start()
        # we expect server's hello message
        init_event.wait()
        # received hello message or an error happened
        self.remove_listener(listener)
        if error[0]:
            raise error[0]
        logger.info('initialized: session-id=%s | server_capabilities=%s' %
                     (self._id, self._server_capabilities))
    
    def add_listener(self, listener):
        logger.debug('installing listener %r' % listener)
        if not isinstance(listener, SessionListener):
            raise SessionError("Listener must be a SessionListener type")
        with self._lock:
            self._listeners.add(listener)
    
    def remove_listener(self, listener):
        logger.debug('discarding listener %r' % listener)
        with self._lock:
            self._listeners.discard(listener)
    
    def get_listener_instance(self, cls):
        with self._lock:
            for listener in self._listeners:
                if isinstance(listener, cls):
                    return listener
    
    def connect(self, *args, **kwds):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
    
    def send(self, message):
        logger.debug('queueing %s' % message)
        self._q.put(message)
    
    ### Properties
    
    @property
    def client_capabilities(self):
        return self._client_capabilities
    
    @property
    def server_capabilities(self):
        return self._server_capabilities
    
    @property
    def connected(self):
        return self._connected
    
    @property
    def id(self):
        "`session-id` if session is initialized, :const:`None` otherwise"
        return self._id
    
    @property
    def can_pipeline(self):
        return True


class SessionListener(object):
    
    def callback(self, root, raw):
        raise NotImplementedError
    
    def errback(self, ex):
        raise NotImplementedError


class HelloHandler(SessionListener):
    
    def __init__(self, init_cb, error_cb):
        self._init_cb = init_cb
        self._error_cb = error_cb
    
    def callback(self, root, raw):
        if content.unqualify(root[0]) == 'hello':
            try:
                id, capabilities = HelloHandler.parse(raw)
            except Exception as e:
                self._error_cb(e)
            else:
                self._init_cb(id, capabilities)
    
    def errback(self, err):
        self._error_cb(err)
    
    @staticmethod
    def build(capabilities):
        "Given a list of capability URI's returns <hello> message XML string"
        spec = {
            'tag': content.qualify('hello'),
            'subtree': [{
                'tag': 'capabilities',
                'subtree': # this is fun :-)
                    [{'tag': 'capability', 'text': uri} for uri in capabilities]
                }]
            }
        return content.dtree2xml(spec)
    
    @staticmethod
    def parse(raw):
        "Returns tuple of (session-id (str), capabilities (Capabilities)"
        sid, capabilities = 0, []
        root = content.xml2ele(raw)
        for child in root.getchildren():
            tag = content.unqualify(child.tag)
            if tag == 'session-id':
                sid = child.text
            elif tag == 'capabilities':
                for cap in child.getchildren():
                    if content.unqualify(cap.tag) == 'capability':
                        capabilities.append(cap.text)
        return sid, Capabilities(capabilities)
