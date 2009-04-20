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

from threading import Event

from listener import Listener

from content import MessageIDParser

class RPC:
    
    cur_id = {}

    def __init__(self, session=None, async=False):
        self._session = None
        self._async = None
        self._reply = None
        self._event = Event()
    
    def get_reply(self, timeout=2.0):
        self._event.wait(timeout)
        if self._event.isSet():
            return self._reply
    
    def do(self, session, async=False):
        self._async = async
    
    def deliver(self, reply):
        self._reply = reply
        self._event.set()

    @property
    def has_reply(self): return self._event.isSet()
    
    @property
    def async(self): return self._async
    
    @property
    def listener(self): return self._listener
    
    def _next_id(self):
        cur_id[self._sid] = cur_id.get(self._sid, 0) + 1
        return cur_id[self._sid]
    
class RPCReply:
    
    def __init__(self, raw):
        self._raw = raw
    
    def get_id(self):
        return content.rpc.parse_msg_id(raw)

class RPCError(NETCONFError):
    
    pass

class ReplyListener(Listener):
    
    def __init__(self):
        self._id2rpc = {}
    
    def reply(self, msg):
        reply = RPCReply(msg)
        id2rpc[reply.get_id()].deliver(reply)
    
    def error(self, buf):
        pass
