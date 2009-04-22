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

logger = logging.getLogger('ncclient.listeners')

session_listeners = {}
def session_listener_factory(session):
    try:
        return session_listeners[session]
    except KeyError:
        session_listeners[session] = SessionListener()
        return session_listeners[session]

class SessionListener(object):
    
    def __init__(self):
        self._id2rpc = WeakValueDictionary()
        self._expecting_close = False
        self._subscription = None
    
    def __str__(self):
        return 'SessionListener'
    
    def set_subscription(self, id):   
        self._subscription = id
    
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
        from ssh import SessionCloseError
        if err is SessionCloseError:
            logger.debug('received session close, expecting_close=%s' %
                         self._expecting_close)
            if not self._expecting_close:
                raise err

class DebugListener:
    
    def __str__(self):
        return 'DebugListener'
    
    def reply(self, raw):
        logger.debug('DebugListener:reply:\n%s' % raw)
    
    def error(self, err):
        logger.debug('DebugListener:error:\n%s' % err)
