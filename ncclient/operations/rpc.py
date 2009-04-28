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

from . import logger

class RPC:
        
    def __init__(self, session, async=False):
        self._session = session
        self._id = uuid1().urn
        self._reply = RPCReply()
        self._reply_event = Event()
    
    def _build(self, op, encoding='utf-8'):
        if isinstance(op, basestring):
            return RPCBuilder.build_from_string(self._id, op, encoding)
        else:
            return RPCBuilder.build_from_spec(self._id, op, encoding)
    
    def _request(self, op):
        self._reply = RPCReply()
        # get the listener instance for this session
        # <rpc-reply> with message id will reach response_cb
        self._listener.register(self._id, self)
        # only effective the first time, transport.session.Subject internally
        # uses a set type for listeners
        self._session.add_listener(self._listener)
        req = RPCBuilder.build(self._id, op)
        self._session.send(req)
        if reply_event is not None: # if we were provided an Event to use
            self._reply_event = reply_event
        else: # otherwise, block till response received and return it
            self._reply_event = Event()
            self._reply_event.wait()
            self._reply.parse()
        return self._reply
    
    def request(self, *args, **kwds):
        raise NotImplementedError
    
    @property
    def has_reply(self):
        try:
            return self._reply_event.isSet()
        except TypeError: # reply_event is None
            return False
    
    @property
    def reply(self):
        return self._reply
    
    @property
    def id(self):
        return self._id
    
    @property
    def session(self):
        return self._session
    
    @staticmethod
    def build_from_spec(msgid, opspec, encoding='utf-8'):
        "TODO: docstring"
        spec = {
            'tag': _('rpc', BASE_NS),
            'attributes': {'message-id': msgid},
            'children': opspec
            }
        return TreeBuilder(spec).to_string(encoding)
    
    @staticmethod
    def build_from_string(msgid, opstr, encoding='utf-8'):
        "TODO: docstring"
        decl = '<?xml version="1.0" encoding="%s"?>' % encoding
        doc = (u'''<rpc message-id="%s" xmlns="%s">%s</rpc>''' %
               (msgid, BASE_NS, opstr)).encode(encoding)
        return (decl + doc)
