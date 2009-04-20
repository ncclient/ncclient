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

import content

from threading import Thread, Event
from Queue import Queue

from capability import CAPABILITIES
from error import ClientError
from subject import Subject

logger = logging.getLogger('ncclient.session')

class SessionError(ClientError):
    
    pass

class Session(Thread, Subject):
    
    def __init__(self):
        Thread.__init__(self, name='session')
        Subject.__init__(self, listeners=[Session.HelloListener(self)])
        self._client_capabilities = CAPABILITIES
        self._server_capabilities = None # yet
        self._id = None # session-id
        self._connected = False
        self._error = None
        self._init_event = Event()
        self._q = Queue()
    
    def connect(self):
        raise NotImplementedError

    def send(self, message):
        message = (u'<?xml version="1.0" encoding="UTF-8"?>%s' % message).encode('utf-8')
        logger.debug('queueing message: \n%s' % message)
        self._q.put(message)

    def run(self):
        raise NotImplementedError
    
    ### Properties

    @property
    def client_capabilities(self):
        return self._client_capabilities
    
    @property
    def serve_capabilities(self):
        return self._server_capabilities
    
    @property
    def connected(self):
        return self._connected
    
    @property
    def id(self):
        return self._id    

    class HelloListener:
        
        def __init__(self, session):
            self._session = session
        
        def _done(self, err=None):
            if err is not None:
                self._session._error = err
            self._session.remove_listener(self)
            self._session._init_event.set()
        
        def reply(self, data):
            err = None
            try:
                id, capabilities = content.parse_hello(data)
                logger.debug('session_id: %s | capabilities: \n%s', id, capabilities)
                self._session._id, self._session.capabilities = id, capabilities
            except Exception as e:
                err = e
            finally:
                self._done(err)
        
        def close(self, err):
            self._done(err)
    
    ### Methods for which subclasses should call super after they are done
    
    def _connect(self):
        self._connected = True
        # start the subclass' main loop
        self.start()
        # queue client's hello message for sending
        self.send(content.make_hello(self._client_capabilities))
        # we expect server's hello message, wait for _init_event to be set by HelloListener
        self._init_event.wait()
        # there may have been an error
        if self._error:
            self._close()
            raise self._error
    
    def _close(self):
        self._connected = False
