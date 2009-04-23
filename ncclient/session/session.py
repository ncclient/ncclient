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
from threading import Thread, Event
from Queue import Queue

import content
from capabilities import Capabilities, CAPABILITIES
from error import ClientError
from listeners import HelloListener
from subject import Subject

logger = logging.getLogger('ncclient.session')

class SessionError(ClientError): pass

class Session(Thread, Subject):
    
    def __init__(self):
        Thread.__init__(self, name='session')
        Subject.__init__(self)
        self._client_capabilities = CAPABILITIES
        self._server_capabilities = None # yet
        self._id = None # session-id
        self._error = None
        self._init_event = Event()
        self._q = Queue()
        self._connected = False # to be set/cleared by subclass implementation
    
    def _post_connect(self):
        # start the subclass' main loop
        listener = HelloListener(self)
        self.add_listener(listener)
        self.start()
        # queue client's hello message for sending
        self.send(content.Hello.build(self._client_capabilities))
        # we expect server's hello message, wait for _init_event to be set
        self._init_event.wait()
        self.remove_listener(listener)
        # there may have been an error
        if self._error:
            self._close()
            raise self._error
    
    def hello(self, id, capabilities):
        self._id, self._capabilities = id, Capabilities(capabilities)
        self._init_event.set()
    
    def hello_error(self, err):
        self._error = err
        self._init_event.set()
    
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
