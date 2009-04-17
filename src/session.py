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
    
    CLIENT, SERVER = range(2)
    
    def __init__(self, capabilities=None, listeners=[]):
        Thread.__init__(self, name='session')
        listeners.append(self)
        Subject.__init__(self, listeners=listeners)
        Thread.setDaemon(True)
        self._capabilities = {
            CLIENT: capabilities,
            SERVER: None # yet
        }
        self._id = None # session-id
        self._connected = False
        self._initialised = False
        self._q = Queue.Queue()
        
    def _init(self, id, capabilities):
        if isinstance(id, int) and isinstance(capabilities, Capabilities):
            self.id = id
            self.capabilities[SERVER] = capabilities
            self.initialised = True
        else:
            raise ValueError
    
    def _greet(self):
        hello = Creator()
        # ...
        self._q.add(hello)
    
    @override
    def _close(self):
        raise NotImplementedError
    
    @override
    def connect(self):
        raise NotImplementedError
    

    def send(self, message):
        if self.ready:
            self._q.add(message)
        else:
            raise SessionError('Session not ready')
    
    ### Thread methods

    @override
    def run(self):
        raise NotImplementedError
    
    ### Listener methods - these are relevant for the initial greeting only
    
    def reply(self, data):
        id, capabilities = None, None
        try:
            p = Parser()
            # ...
            self._init(id, capabilities)
        except: # ...
            pass
        finally:
            self.remove_listener(self)
    
    def error(self, data):
        self._close()
        raise SSHError('Session initialization failed')

    ### Getter methods and properties

    def get_capabilities(self, whose):
        return self._capabilities[whose]
    
    @property
    def ready(self): self._connected and self._initialised
    
    @property
    def id(self): self._id    
    
    @property
    def client_capabilities(self):
        return self._capabilities[CLIENT]
    
    @property
    def server_capabilities(self):
        return self._capabilities[SERVER]
