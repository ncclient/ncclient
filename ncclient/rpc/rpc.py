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

from threading import Event, Lock
from uuid import uuid1
from weakref import WeakValueDictionary

from ncclient.content import XMLConverter
from ncclient.content import qualify as _
from ncclient.content import unqualify as __
from ncclient.glue import Listener

from listener import RPCReplyListener
from reply import RPCReply

import logging
logger = logging.getLogger('ncclient.rpc')

class RPC(object):
    
    DEPENDS = []
    REPLY_CLS = RPCReply
    
    def __init__(self, session, async=False, timeout=None):
        if not session.can_pipeline:
            raise UserWarning('Asynchronous mode not supported for this device/session')
        self._session = session
        try:
            for cap in self.DEPENDS:
                self.assert_capability(cap)
        except AttributeError:
            pass        
        self._async = async
        self._timeout = timeout
        self._id = uuid1().urn
        self._listener = RPCReplyListener(session)
        self._listener.register(self._id, self)
        self._reply = None
        self._reply_event = Event()
    
    def _build(self, opspec, encoding='utf-8'):
        "TODO: docstring"
        spec = {
            'tag': _('rpc'),
            'attributes': {'message-id': self._id},
            'children': opspec
            }
        return XMLConverter(spec).to_string(encoding)
    
    def _request(self, op):
        req = self._build(op)
        self._session.send(req)
        if self._async:
            return self._reply_event
        else:
            self._reply_event.wait(self._timeout)
            if self._reply_event.isSet():
                self._reply.parse()
                return self._reply
            else:
                raise ReplyTimeoutError
    
    def _delivery_hook(self):
        'For subclasses'
        pass
    
    def _assert(self, capability):
        if capability not in self._session.server_capabilities:
            raise MissingCapabilityError('Server does not support [%s]' % cap)
    
    def deliver(self, raw):
        self._reply = self.REPLY_CLS(raw)
        self._delivery_hook()
        self._reply_event.set()
    
    @property
    def has_reply(self):
        return self._reply_event.isSet()
    
    @property
    def reply(self):
        return self._reply
    
    @property
    def id(self):
        return self._id
    
    @property
    def session(self):
        return self._session
    
    @property
    def reply_event(self):
        return self._reply_event
    
    def set_async(self, bool): self._async = bool
    async = property(fget=lambda self: self._async, fset=set_async)
    
    def set_timeout(self, timeout): self._timeout = timeout
    timeout = property(fget=lambda self: self._timeout, fset=set_timeout)
