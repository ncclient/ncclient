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

'Remote Procedure Call'

from threading import Event, Lock
from uuid import uuid1

_listeners = WeakValueDictionary()

def get_listener(session):
    try:
        return _listeners[session]
    except KeyError:
        _listeners[session] = MessageListener()
        return _listeners[session]

class RPC:
    
    def __init__(self, session, async=False, parse=True):
        self._session = session
        self._async = async
        self._id = uuid1().urn
        self._reply = None
        self._reply_event = Event()
        self.listener.register(self._id, self)
        session.add_listener(self.listener)

    def _response_cb(self, reply):
        self._reply = reply
        self._event.set()
    
    def _do_request(self, operation):
        'operation is xml string'
        self._session.send(content.RPC.make(self._id, operation))
        if not self._async:
            self._reply_event.wait()
        return self._reply
    
    def request(self):
        raise NotImplementedError
    
    def wait_for_reply(self, timeout=None):
        self._reply_event.wait(timeout)
    
    @property
    def has_reply(self):
        return self._reply_event.isSet()
    
    @property
    def is_async(self):
        return self._async
    
    @property
    def reply(self):
        return self._reply
    
    @property
    def id(self):
        return self._id
    
    @property
    def listener(self):
        listener = get_listener(self._session)

    @property
    def session(self):
        return self._session

class RPCReply:
    
    class RPCError:
        
        pass
    

class MessageListener:
    
    def __init__(self):
        # {message-id: RPC}
        self._rpc = WeakValueDictionary()
        # if the session gets closed by remote endpoint,
        # need to know if it is an error event or was requested through
        # a NETCONF operation i.e. CloseSession
        self._expecting_close = False
        # other recognized names and behavior on receiving them
        self._recognized = []
    
    def __str__(self):
        return 'MessageListener'
    
    def expect_close(self):
        self._expecting_close = True
    
    def register(self, id, op):
        self._id2rpc[id] = op
    
    ### Events
    
    def reply(self, raw):
        pass
    
    def error(self, err):
        from ncclient.session.session import SessionCloseError
        if err is SessionCloseError:
            logger.debug('session closed by remote endpoint, expecting_close=%s' %
                         self._expecting_close)
            if not self._expecting_close:
                raise err

