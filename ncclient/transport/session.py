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

from threading import Thread, Lock, Event
from Queue import Queue

from . import logger
from ncclient.capabilities import Capabilities, CAPABILITIES


class Subject:

    def __init__(self):
        self._listeners = set([])
        self._lock = Lock()
        
    def has_listener(self, listener):
        with self._lock:
            return (listener in self._listeners)
    
    def add_listener(self, listener):
        with self._lock:
            self._listeners.add(listener)
    
    def remove_listener(self, listener):
        with self._lock:
            self._listeners.discard(listener)
    
    def dispatch(self, event, *args, **kwds):
        # holding the lock while doing callbacks could lead to a deadlock
        # if one of the above methods is called
        with self._lock:
            listeners = list(self._listeners)
        for l in listeners:
            try:
                logger.debug('dispatching [%s] to [%s]' % (event, l))
                getattr(l, event)(*args, **kwds)
            except Exception as e:
                pass # if a listener doesn't care for some event we don't care


class Session(Thread, Subject):
    
    def __init__(self):
        Thread.__init__(self, name='session')
        Subject.__init__(self)
        self._client_capabilities = CAPABILITIES
        self._server_capabilities = None # yet
        self._id = None # session-id
        self._q = Queue()
        self._connected = False # to be set/cleared by subclass implementation
    
    def _post_connect(self):
        from ncclient.content.builders import HelloBuilder
        self.send(HelloBuilder.build(self._client_capabilities))
        error = None
        init_event = Event()
        def ok_cb(id, capabilities):
            self._id, self._capabilities = id, Capabilities(capabilities)
            init_event.set()
        def err_cb(err):
            error = err
            init_event.set()
        listener = HelloListener(ok_cb, err_cb)
        self.add_listener(listener)
        # start the subclass' main loop
        self.start()        
        # we expect server's hello message
        init_event.wait()
        # received hello message or an error happened
        self.remove_listener(listener)
        if error:
            raise error
        logger.debug('initialized:session-id:%s' % self._id)
    
    def send(self, message):
        logger.debug('queueing:%s' % message)
        self._q.put(message)
    
    def connect(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
        
    def capabilities(self, whose='client'):
        if whose == 'client':
            return self._client_capabilities
        elif whose == 'server':
            return self._server_capabilities
    
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
        return self._id


class HelloListener:
    
    def __init__(self, init_cb, error_cb):
        self._init_cb, self._error_cb = init_cb, error_cb
    
    def __str__(self):
        return 'HelloListener'
    
    ### Events
    
    def received(self, raw):
        logger.debug(raw)
        from ncclient.content.parsers import HelloParser
        try:
            id, capabilities = HelloParser.parse(raw)
        except Exception as e:
            self._error_cb(e)
        else:
            self._init_cb(id, capabilities)
    
    def error(self, err):
        self._error_cb(err)


class DebugListener:
    
    def __str__(self):
        return 'DebugListener'
    
    def received(self, raw):
        logger.info('DebugListener:[received]:%s' % raw)
    
    def error(self, err):
        logger.info('DebugListener:[error]:%s' % err)
