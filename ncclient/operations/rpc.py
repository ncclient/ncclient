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

from ncclient.content import TreeBuilder
from ncclient.content import qualify as _
from ncclient.content import unqualify as __
from ncclient.glue import Listener

from . import logger
from reply import RPCReply

# Cisco does not include message-id attribute in <rpc-reply> in case of an error.
# This is messed up however we have to deal with it.
# So essentially, there can be only one operation at a time if we are talking to
# a Cisco device.

class RPC(object):
    
    def __init__(self, session, async=False):
        if session.is_remote_cisco and async:
            raise UserWarning('Asynchronous mode not supported for Cisco devices')
        self._session = session
        self._async = async
        self._id = uuid1().urn
        self._listener = RPCReplyListener(session)
        self._listener.register(self._id, self)
        self._reply = None
        self._reply_event = Event()
    
    def _build(self, op, encoding='utf-8'):
        if isinstance(op, dict):
            return self.build_from_spec(self._id, op, encoding)
        else:
            return self.build_from_string(self._id, op, encoding)
    
    def _request(self, op):
        req = self._build(op)
        self._session.send(req)
        if self._async:
            return self._reply_event
        else:
            self._reply_event.wait()
            self._reply.parse()
            return self._reply
    
    def _delivery_hook(self):
        'For subclasses'
        pass
    
    def deliver(self, raw):
        self._reply = RPCReply(raw)
        self._delivery_hook()
        self._reply_event.set()
    
    @property
    def has_reply(self):
        return self._reply_event.isSet()
    
    @property
    def reply(self):
        return self._reply
    
    @property
    def is_async(self):
        return self._async
    
    @property
    def id(self):
        return self._id
    
    @property
    def session(self):
        return self._session
    
    @property
    def reply_event(self):
        return self._reply_event
    
    @staticmethod
    def build_from_spec(msgid, opspec, encoding='utf-8'):
        "TODO: docstring"
        spec = {
            'tag': _('rpc'),
            'attributes': {'message-id': msgid},
            'children': opspec
            }
        return TreeBuilder(spec).to_string(encoding)
    
    @staticmethod
    def build_from_string(msgid, opstr, encoding='utf-8'):
        "TODO: docstring"
        decl = '<?xml version="1.0" encoding="%s"?>' % encoding
        doc = (u'<rpc message-id="%s" xmlns="%s">%s</rpc>' %
               (msgid, BASE_NS, opstr)).encode(encoding)
        return '%s%s' % (decl, doc)


class RPCReplyListener(Listener):
    
    # TODO - determine if need locking
    
    # one instance per session
    def __new__(cls, session):
        instance = session.get_listener_instance(cls)
        if instance is None:
            instance = object.__new__(cls)
            instance._id2rpc = WeakValueDictionary()
            instance._cisco = session.is_remote_cisco
            instance._errback = None
            session.add_listener(instance)
        return instance
    
    def __str__(self):
        return 'RPCReplyListener'
    
    def set_errback(self, errback):
        self._errback = errback

    def register(self, id, rpc):
        self._id2rpc[id] = rpc
    
    def callback(self, root, raw):
        tag, attrs = root
        if __(tag) != 'rpc-reply':
            return
        rpc = None
        for key in attrs:
            if __(key) == 'message-id':
                id = attrs[key]
                try:
                    rpc = self._id2rpc.pop(id)
                except KeyError:
                    logger.warning('[RPCReplyListener.callback] no object '
                                   + 'registered for message-id: [%s]' % id)
                except Exception as e:
                    logger.debug('[RPCReplyListener.callback] error - %r' % e)
                break
        else:
            if self._cisco:
                assert(len(self._id2rpc) == 1)
                rpc = self._id2rpc.values()[0]
                self._id2rpc.clear()
            else:
                logger.warning('<rpc-reply> without message-id received: %s' % raw)
        logger.debug('[RPCReplyListener.callback] delivering to %r' % rpc)
        rpc.deliver(raw)
    
    def errback(self, err):
        if self._errback is not None:
            self._errback(err)
