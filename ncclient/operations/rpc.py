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
from weakref import WeakKeyDictionary, WeakValueDictionary

from listener import get_listener
from ncclient.content.builders import RPCBuilder
from ncclient.content.parsers import RootParser
from ncclient.content.common import qualify as _
from ncclient.content.common import BASE_NS

class RPC:
    
    _listeners = WeakKeyDictionary()
    _lock = Lock()
    
    def __init__(self, session):
        self._session = session
        self._id = None
        self._reply = None # RPCReply
        self._reply_event = None
    
    @property
    def _listener(self):
        with self._lock:
            return self._listeners.setdefault(self._session, MessageListener())
    
    def _response_cb(self, raw):
        self._reply = RPCReply(raw)
        reply_event.set()
    
    def _do_request(self, op, reply_event=None):
        self._id = uuid1().urn
        # get the listener instance for this session
        # <rpc-reply> with message id will reach response_cb
        self._listener.register(self._id, self._response_cb)
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

class RPCReply:
    
    def __init__(self, raw):
        self._raw = raw
        self._parsed = False
        self._ok = None
        self._errs = []
    
    def __str__(self):
        return self._raw

    @property
    def raw(self):
        return self._raw
    
    def parse(self):
        #errs = RPCParser.parse(self._raw)
        #for raw, err_dict in errs:
        #    self._errs.append(RPCError(raw, err_dict))
        self._parsed = True
    
    @property
    def parsed(self):
        return self._parsed
    
    @property
    def ok(self):
        return True if self._parsed and not self._err else False
    
    @property
    def errors(self):
        return self._errs
    
    @property
    def raw(self):
        return self._raw

class RPCError(Exception): # raise it if you like
    
    def __init__(self, raw, err_dict):
        self._raw = raw
        self._dict = err_dict

    def __str__(self):
        # TODO
        return self._raw
    
    def __dict__(self):
        return self._dict
    
    @property
    def raw(self):
        return self._raw
    
    @property
    def type(self):
        return self._dict.get('type', None)
    
    @property
    def severity(self):
        return self._dict.get('severity', None)
    
    @property
    def tag(self):
        return self._dict.get('tag', None)
    
    @property
    def path(self):
        return self._dict.get('path', None)
    
    @property
    def message(self):
        return self._dict.get('message', None)
    
    @property
    def info(self):
        return self._dict.get('info', None)


class SessionListener:
    
    '''This is the glue between received data and the object it should be
    forwarded to.
    '''
    
    def __init__(self):
        # this dictionary takes care of <rpc-reply> elements received
        # { 'message-id': callback } dict
        self._id2cb = WeakValueDictionary()
        # this is a more generic dict takes care of other top-level elements
        # that may be received, e.g. <notification>'s
        # {'tag': callback} dict
        self._tag2cb = WeakValueDictionary() 
        # if we receive a SessionCloseError it might not be one we want to act on
        self._expecting_close = False
        self._errback = None # error event callback
        self._lock = Lock()
    
    def __str__(self):
        return 'SessionListener'
    
    def register(self, msgid, cb):
        with self._lock:
            self._id2cb[msgid] = cb
    
    def recognize(self, tag, cb):
        with self._lock:
            self._tag2cb[tag] = cb
    
    def expect_close(self):
        self._expecting_close = True
    
    @property
    def _recognized_elements(self):
        elems = [_('rpc-reply', BASE_NS)]
        with self._lock:
            elems.extend(self._tag2cb.keys())
        return elems
    
    def reply(self, raw):
        tag, attrs = RootParser.parse(raw, self._recognized_elements)
        try:
            cb = None
            if tag == _('rpc-reply', BASE_NS):
                try:
                    id = attrs[_('message-id', BASE_NS)]
                except KeyError:
                    logger.warning('<rpc-reply> w/o message-id attr received: %s'
                                   % raw)
                cb = self._id2cb.get(id, None)
            else:
                cb = self._tag2cb.get(tag, None)
            if cb is not None:
                cb(raw)
        except Exception as e:
            logger.warning('SessionListener.reply: %r' % e)
    
    def set_errback(self, errback):
        self._errback = errback
    
    def error(self, err):
        from ncclient.transport.error import SessionCloseError
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
