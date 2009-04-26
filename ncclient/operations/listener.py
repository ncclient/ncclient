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

from threading import Lock
from weakref import WeakValueDictionary

from . import logger
from ncclient.content.parsers import RootParser
from ncclient.content.common import qualify as _
from ncclient.content.common import unqualify as __
from ncclient.content.common import BASE_NS, CISCO_BS

q_rpcreply = [_('rpc-reply', BASE_NS), _('rpc-reply', CISCO_BS)]

class SessionListener:
    
    '''This is the glue between received data and the object it should be
    forwarded to.
    '''
    
    def __init__(self):
        # this dictionary takes care of <rpc-reply> elements received
        # { 'message-id': obj } dict
        self._id2rpc = WeakValueDictionary()
        # this is a more generic dict takes care of other top-level elements
        # that may be received, e.g. <notification>'s
        # {'tag': obj} dict
        self._tag2obj = WeakValueDictionary() 
        # if we receive a SessionCloseError it might not be one we want to act on
        self._expecting_close = False
        self._errback = None # error event callback
        self._lock = Lock()
    
    def __str__(self):
        return 'SessionListener'
    
    def register(self, msgid, rpc):
        with self._lock:
            self._id2rpc[msgid] = rpc
    
    def recognize(self, tag, obj):
        with self._lock:
            self._tag2obj[tag] = obj
    
    def expect_close(self):
        self._expecting_close = True
    
    @property
    def _recognized_elements(self):
        elems = q_rpcreply
        with self._lock:
            elems.extend(self._tag2obj.keys())
        return elems
    
    def set_errback(self, errback):
        self._errback = errback
    
    def received(self, raw):
        res = RootParser.parse(raw, self._recognized_elements)
        if res is not None:
            tag, attrs = res # unpack
        else:
            return
        logger.debug('SessionListener.reply: parsed (%r, %r)' % res)
        try:
            obj = None
            if tag in q_rpcreply:
                for key in attrs:
                    if __(key) == 'message-id':
                        id = attrs[key]
                        break
                else:
                    logger.warning('<rpc-reply> without message-id received: %s'
                                   % raw)
                obj = self._id2rpc.get(id, None)
            else:
                obj = self._tag2obj.get(tag, None)
            if obj is not None:
                obj.deliver(raw)
        except Exception as e:
            logger.warning('SessionListener.reply: %r' % e)
    
    def error(self, err):
        from ncclient.transport.errors import SessionCloseError
        act = True
        if isinstance(err, SessionCloseError):
            logger.debug('session closed, expecting_close=%s' %
                         self._expecting_close)
            if self._expecting_close:
                act = False
        if act:
            logger.error('SessionListener.error: %r' % err)
            if self._errback is not None:
                errback(err)
