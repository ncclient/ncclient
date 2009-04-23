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
from weakref import WeakValueDictionary

import content
from session import SessionCloseError

logger = logging.getLogger('ncclient.listeners')

################################################################################

# {session-id: SessionListener}
session_listeners = WeakValueDictionary
def session_listener_factory(session):
    try:
        return session_listeners[session]
    except KeyError:
        session_listeners[session] = SessionListener()
        return session_listeners[session]

class SessionListener:
    
    def __init__(self):
        # {message-id: RPC}
        self._rpc = WeakValueDictionary()
        # if the session gets closed by remote endpoint,
        # need to know if it is an error event or was requested through
        # a NETCONF operation i.e. CloseSession
        self._expecting_close = False
        # other recognized names 
        self._recognized = []
    
    def __str__(self):
        return 'SessionListener'
    
    def expect_close(self):
        self._expecting_close = True
    
    def register(self, id, op):
        self._id2rpc[id] = op
    
    ### Events
    
    def reply(self, raw):
        try:
            id = content.parse_message_root(raw)
            if id is None:
                pass
            elif id == 'notification':
                self._id2rpc[self._sub_id]._notify(raw)
            else:
                self._id2rpc[id]._response_cb(raw)
        except Exception as e:
            logger.warning(e)
    
    def error(self, err):
        if err is SessionCloseError:
            logger.debug('session closed by remote endpoint, expecting_close=%s' %
                         self._expecting_close)
            if not self._expecting_close:
                raise err

################################################################################

class HelloListener:
    
    def __str__(self):
        return 'HelloListener'
        
    def __init__(self, session):
        self._session = session
    
    ### Events
    
    def reply(self, data):
        try:
            id, capabilities = content.Hello.parse(data)
            logger.debug('HelloListener: session_id: %s; capabilities: %s', id, capabilities)
            self._session.initialize(id, capabilities)
        except Exception as e:
            self._session.initialize_error(e)
    
    def error(self, err):
        self._session.initialize_error(err)

################################################################################

class DebugListener:
    def __str__(self): return 'DebugListener'
    def reply(self, raw): logger.debug('DebugListener:reply:\n%s' % raw)
    def error(self, err): logger.debug('DebugListener:error:\n%s' % err)
