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
        self._error = False
        self._q = Queue.Queue()
        
    def _init(self, id, capabilities):
        self.id = id
        self.capabilities[SERVER] = capabilities
        self.initialised = True
    
    def _greet(self):
        hello = Creator()
        # ...
        self._q.add(hello)
    
    def _close(self):
        raise NotImplementedError
    
    def connect(self):
        raise NotImplementedError

    def send(self, message):
        'Blocks if session not initialised yet'
        while not (self.ready or self._error):
            time.sleep(0.1)
        if self._error:
            raise SessionError
        else:
            self._q.add(message)

    def run(self):
        raise NotImplementedError
    
    ### Listener methods - relevant for the initial greeting
    
    def reply(self, data, *args, **kwds):
        id, capabilities = None, None
        try:
            p = Parser()
            # ...
            self._init(id, capabilities)
        except:
            self._error = True
        finally:
            self.remove_listener(self)
    
    def error(self, data, *args, **kwds):
        self._close()
        self.remove_listener(self)
        self._error = True
    
    ### Properties

    @property
    def client_capabilities(self): return self._capabilities[CLIENT]
    
    @property
    def serve_capabilities(self): return self._capabilities[SERVER]
    
    @property
    def ready(self): return (self._connected and self._initialised)
    
    @property
    def id(self): return self._id
    