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
        
    def connect(self):
        self.start()
        
    def run(self):
        raise NotImplementedError
        
    def send(self, msg):
        if not self.connected:
            self._q.add(msg)

    def expectClose(self, val=True):
        '''operations.CloseSession must call this before a call to send(),
        so that the remote endpoint closing the connection does not result
        in an exception'''
        self._expectClose = val

    @property
    def id(self):
        'Session ID'
        return self._id
    
    # Preferred way is to access the attributes directly,
    # but here goes:
    
    # TODO