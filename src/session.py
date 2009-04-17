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

from content import Creator, Parser

from threading import Thread
from listener import Subject, Listener

class SessionError(ncclientError): pass

class Session(Thread, Subject, Listener):
    
    def __init__(self, capabilities=None):
        Thread.__init__(self, name='session')
        Subject.__init__(self, listeners=[self])
        Thread.setDaemon(True)
        self.client_capabilities = capabilities
        self.server_capabilities = None # yet
        self.id = None # session-id
        self.connected = False
        self.initialised = False
        self._q = Queue.Queue()
        
    def _init(self, id, capabilities):
        self.id = id
        self.capabilities[SERVER] = capabilities
        self.initialised = True
    
    def _greet(self):
        self._q.add(make_hello())
    
    @override
    def _close(self):
        raise NotImplementedError
    
    @override
    def connect(self):
        'call Session.connect() at the end'
        self._greet()
        Thread.start()
    
    def send(self, msg):
        if self.connected and self.initialised:
            self._q.add(msg)
        else:
            raise SessionError('Attempted to send message while not connected')
        
    ### Thread methods

    @override
    def run(self):
        raise NotImplementedError
    
    ### Subject methods
    
    def add_listener(self, listener):
        if not self.initialised:
            raise SessionError('Listeners may only be added after session initialisation')
        else:
            Subject.add_listner(self, listener)
    
    ### Listener methods
    # these are relevant for the initial greeting only
    
    def reply(self, data):
        p = Parser(data)
        s = p['session']
        id = s['@id']
        capabilities = Capabilities()
        capabilities.fromXML(p['capabilities'])
        self._init(id, capabilities)
        self.remove_listener(self)
    
    def error(self, data):
        self._close()
        raise SSHError('Session initialization failed')
    