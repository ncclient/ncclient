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

from ncclient import content
from ncclient.transport import SessionListener

from errors import OperationError

import logging
logger = logging.getLogger('ncclient.rpc')


class RPCReply:
    
    'NOTES: memory considerations?? storing both raw xml + ET.Element'
    
    def __init__(self, raw):
        self._raw = raw
        self._parsed = False
        self._root = None
        self._errors = []
    
    def __repr__(self):
        return self._raw
    
    def _parsing_hook(self, root):
        pass
    
    def parse(self):
        if self._parsed:
            return
        root = self._root = content.xml2ele(self._raw) # <rpc-reply> element
        # per rfc 4741 an <ok/> tag is sent when there are no errors or warnings
        ok = content.find(root, 'data', strict=False)
        if ok is not None:
            logger.debug('parsed [%s]' % ok.tag)
        else: # create RPCError objects from <rpc-error> elements
            error = content.find(root, 'data', strict=False)
            if error is not None:
                logger.debug('parsed [%s]' % error.tag)
                for err in root.getiterator(error.tag):
                    # process a particular <rpc-error>
                    d = {}
                    for err_detail in err.getchildren(): # <error-type> etc..
                        tag = content.unqualify(err_detail.tag)
                        if tag != 'error-info':
                            d[tag] = err_detail.text.strip()
                        else:
                            d[tag] = content.ele2xml(err_detail)
                    self._errors.append(RPCError(d))
        self._parsing_hook(root)
        self._parsed = True
    
    @property
    def xml(self):
        '<rpc-reply> as returned'
        return self._raw
    
    @property
    def ok(self):
        if not self._parsed:
            self.parse()
        return not self._errors # empty list => false
    
    @property
    def error(self):
        if not self._parsed:
            self.parse()
        if self._errors:
            return self._errors[0]
        else:
            return None
    
    @property
    def errors(self):
        'List of RPCError objects. Will be empty if no <rpc-error> elements in reply.'
        if not self._parsed:
            self.parse()
        return self._errors


class RPCError(OperationError): # raise it if you like
    
    def __init__(self, err_dict):
        self._dict = err_dict
        if self.message is not None:
            OperationError.__init__(self, self.message)
        else:
            OperationError.__init__(self)
    
    @property
    def type(self):
        return self.get('error-type', None)
    
    @property
    def severity(self):
        return self.get('error-severity', None)
    
    @property
    def tag(self):
        return self.get('error-tag', None)
    
    @property
    def path(self):
        return self.get('error-path', None)
    
    @property
    def message(self):
        return self.get('error-message', None)
    
    @property
    def info(self):
        return self.get('error-info', None)

    ## dictionary interface
    
    __getitem__ = lambda self, key: self._dict.__getitem__(key)
    
    __iter__ = lambda self: self._dict.__iter__()
    
    __contains__ = lambda self, key: self._dict.__contains__(key)
    
    keys = lambda self: self._dict.keys()
    
    get = lambda self, key, default: self._dict.get(key, default)
        
    iteritems = lambda self: self._dict.iteritems()
    
    iterkeys = lambda self: self._dict.iterkeys()
    
    itervalues = lambda self: self._dict.itervalues()
    
    values = lambda self: self._dict.values()
    
    items = lambda self: self._dict.items()
    
    __repr__ = lambda self: repr(self._dict)


class RPCReplyListener(SessionListener):
    
    # one instance per session
    def __new__(cls, session):
        instance = session.get_listener_instance(cls)
        if instance is None:
            instance = object.__new__(cls)
            instance._lock = Lock()
            instance._id2rpc = WeakValueDictionary()
            instance._pipelined = session.can_pipeline
            session.add_listener(instance)
        return instance
    
    def register(self, id, rpc):
        with self._lock:
            self._id2rpc[id] = rpc
    
    def callback(self, root, raw):
        tag, attrs = root
        if content.unqualify(tag) != 'rpc-reply':
            return
        rpc = None
        for key in attrs:
            if content.unqualify(key) == 'message-id':
                id = attrs[key]
                try:
                    with self._lock:
                        rpc = self._id2rpc.pop(id)
                except KeyError:
                    logger.warning('no object registered for message-id: [%s]' % id)
                except Exception as e:
                    logger.debug('error - %r' % e)
                break
        else:
            if not self._pipelined:
                with self._lock:
                    assert(len(self._id2rpc) == 1)
                    rpc = self._id2rpc.values()[0]
                    self._id2rpc.clear()
            else:
                logger.warning('<rpc-reply> without message-id received: %s' % raw)
        logger.debug('delivering to %r' % rpc)
        rpc.deliver(raw)
    
    def errback(self, err):
        for rpc in self._id2rpc.values():
            rpc.error(err)


class RPC(object):
    
    DEPENDS = []
    REPLY_CLS = RPCReply
    
    def __init__(self, session, async=False, timeout=None):
        if not session.can_pipeline:
            raise UserWarning('Asynchronous mode not supported for this device/session')
        self._session = session
        try:
            for cap in self.DEPENDS:
                self._assert(cap)
        except AttributeError:
            pass        
        self._async = async
        self._timeout = timeout
        # keeps things simple instead of having a class attr that has to be locked
        self._id = uuid1().urn
        # RPCReplyListener itself makes sure there isn't more than one instance -- i.e. multiton
        self._listener = RPCReplyListener(session)
        self._listener.register(self._id, self)
        self._reply = None
        self._reply_event = Event()
    
    def _build(self, opspec):
        "TODO: docstring"
        spec = {
            'tag': content.qualify('rpc'),
            'attributes': {'message-id': self._id},
            'subtree': opspec
            }
        return content.dtree2xml(spec)
    
    def _request(self, op):
        req = self._build(op)
        self._session.send(req)
        if self._async:
            return (self._reply_event, self._error_event)
        else:
            self._reply_event.wait(self._timeout)
            if self._reply_event.is_set():
                if self._error:
                    raise self._error
                self._reply.parse()
                return self._reply
            else:
                raise ReplyTimeoutError
    
    def request(self):
        return self._request(self.SPEC)
    
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
    
    def error(self, err):
        self._error = err
        self._reply_event.set()
    
    @property
    def has_reply(self):
        return self._reply_event.is_set()
    
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
