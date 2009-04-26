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
from weakref import WeakKeyDictionary

from listener import SessionListener
from ncclient.content.builders import RPCBuilder
from ncclient.content.parsers import RPCReplyParser

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
            return self._listeners.setdefault(self._session, SessionListener())
    
    def deliver(self, raw):
        self._reply = RPCReply(raw)
        self._reply_event.set()
    
    def _do_request(self, op, reply_event=None):
        self._id = uuid1().urn
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

class RPCReply:
    
    def __init__(self, raw):
        self._raw = raw
        self._parsed = False
        self._errs = []
    
    def __str__(self):
        return self._raw
    
    def parse(self):
        if not self._parsed:
            errs = RPCReplyParser.parse(self._raw)
            for raw, err_dict in errs:
                self._errs.append(RPCError(raw, err_dict))
            self._parsed = True
    
    @property
    def raw(self):
        return self._raw
    
    @property
    def parsed(self):
        return self._parsed
    
    @property
    def ok(self):
        return True if self._parsed and not self._errs else False
    
    @property
    def errors(self):
        return self._errs

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
