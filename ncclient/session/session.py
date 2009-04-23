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

import logging
from threading import Thread, Lock, Event
from Queue import Queue

from capabilities import Capabilities, CAPABILITIES

logger = logging.getLogger('ncclient.session')

class SessionError(Exception):
    
    pass

class SessionCloseError(SessionError):
    
    def __init__(self, in_buf, out_buf=None):
        SessionError.__init__(self)
        self._in_buf, self._out_buf = in_buf, out_buf
        
    def __str__(self):
        msg = 'Session closed by remote endpoint.'
        if self._in_buf:
            msg += '\nIN_BUFFER: %s' % self._in_buf
        if self._out_buf:
            msg += '\nOUT_BUFFER: %s' % self._out_buf
        return msg
    
class Session(Thread):
    
    def __init__(self):
        Thread.__init__(self, name='session')
        self._client_capabilities = CAPABILITIES
        self._server_capabilities = None # yet
        self._id = None # session-id
        self._q = Queue()
        self._connected = False # to be set/cleared by subclass implementation
        self._listeners = set([])
        self._lock = Lock()
    
    def _post_connect(self):
        from ncclient.content.builders import HelloBuilder
        # queue client's hello message for sending
        self.send(HelloBuilder.build(self._client_capabilities))
        
        error = None
        proceed = Event()
        def ok_cb(id, capabilities):
            self._id, self._capabilities = id, Capabilities(capabilities)
            proceed.set()
        def err_cb(err):
            error = err
            proceed.set()
        listener = HelloListener(ok_cb, err_cb)
        self.add_listener(listener)
        
        # start the subclass' main loop
        self.start()        
        # we expect server's hello message
        proceed.wait()
        # received hello message or an error happened
        self.remove_listener(listener)
        if error:
            self._close()
            raise self._error
    
    def send(self, message):
        logger.debug('queueing message: \n%s' % message)
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
    
    ### Session is a subject for arbitary listeners
    
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
                logger.warning(e)
    
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
    
    def reply(self, raw):
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
    
    def reply(self, raw):
        logger.debug('DebugListener:reply:%s' % raw)
    
    def error(self, err):
        logger.debug('DebugListener:error:%s' % err)
