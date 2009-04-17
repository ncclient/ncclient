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

from listener import Listener

from threading import Event

class OperationError(NETCONFError): pass

class RPC:
    pass

class RPCRequest(RPC):
    
    cur_msg_id = {}

    @cls
    def next_id(cls, session_id):
        cur_msg_id[session_id] = cur_msg_id.get(session_id, 0) + 1
        return cur_msg_id[session_id]

    def __init__(self):
        self._reply = None
        self._event = Event()
        self._async = None

    def get_reply(self, timeout=2.0):
        self._event.wait(timeout)
        if self._event.isSet():
            return self._reply

    def do(self, session, async=False):
        self._async = async
        
    @property
    def async(self):
        return self._async
    
class RPCReply(RPC):
    pass

class RPCError(OperationError):
    pass

class Operation(RPCRequest):
    pass

class ReplyListener(Listener):
    
    def __init__(self):
        self._id2op = {}
    
    def reply(self, msg):
        # if all good:
        op = id2op[id]
        op._reply = parsed_msg
        # else:
        self._error = True
        
        op._event.set()
        pass
    
    def error(self, buf):
        pass
