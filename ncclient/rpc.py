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

import content

from threading import Event

from listener import RPCReplyListener

class RPC:
    
    current_id = {}
    listeners = {}

    def __init__(self, session=None, async=False):
        self._session = None
        self._async = None
        self._reply = None
        self._event = Event()
    
    def get_reply(self, timeout=2.0):
        self._event.wait(timeout)
        if self._event.isSet():
            return self._reply
    
    def do(self, async=False):
        self._async = async
    
    def _deliver(self, reply):
        self._reply = reply
        self._event.set()

    @property
    def has_reply(self):
        return self._event.isSet()
    
    @property
    def is_async(self):
        return self._async
    
    @property
    def listener(self):
        if RPC.listeners[self._sid] is None:
            RPC.listeners[self.sid] = listener.RPCReplyListener()
        return RPC.listeners[self._sid]
    
    @property
    def ok(self):
        pass
    
    def _next_id(self):
        RPC.current_id[self._session.id] = RPC.current_id.get(self._session.id, 0) + 1
        return RPC.current_id[self._sid]
    
class RPCReply:
    
    def __init__(self, id, raw):
        self._id = id
        self._raw = raw
    
    @property
    def id(self):
        return self._id
    
class RPCError(NETCONFError):
    pass
