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

import threading

class SessionError(NETCONFClientError): pass

class Session(threading.Thread):
    
    def __init__(self, capabilities, reply_cb):
        Thread.__init__(self)
        self.capabilities = {
            'client': capabilities,
            'server': None #yet
            }
        self._q = Queue.Queue()
        self._cb = reply_cb
        self.id = None # session-id
        self.connected = False
    
    def _make_hello(self):
        pass
    
    def _parse_hello(self, msg):
        pass
    
    def connect(self):
        self.start()
        
    def run(self):
        raise NotImplementedError
        
    def send(self, msg):
        if self.connected:
            self._q.add(msg)
        else:
            raise SessionError('''Attempted to send message before
                               NETCONF session initialisation''')
            