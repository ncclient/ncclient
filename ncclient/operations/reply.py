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

def parse():
    
    pass


class RPCReply:
    
    def __init__(self, event):
        self._raw = None
        self._errs = None
    
    def __str__(self):
        return self._raw
    
    def parse(self):
        if not self._parsed:
            ok = RPCReplyParser.parse(self._raw)
            for err in errs:
                self._errs.append(RPCError(*err))
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


class RPCReplyListener(Listener):
    
    # TODO - determine if need locking
    
    # one instance per subject    
    def __new__(cls, subject):
        instance = subject.get_listener_instance(cls)
        if instance is None:
            instance = object.__new__(cls)
            instance._id2rpc = WeakValueDictionary()
            instance._errback = None
            subject.add_listener(instance)
        return instance
    
    def __str__(self):
        return 'RPCReplyListener'
    
    def set_errback(self, errback):
        self._errback = errback

    def register(self, msgid, rpc):
        self._id2rpc[msgid] = rpc
    
    def callback(self, root, raw):
        tag, attrs = root
        if __(tag) != 'rpc-reply':
            return
        for key in attrs:
            if __(key) == 'message-id':
                id = attrs[key]
                try:
                    rpc = self._id2rpc[id]
                    rpc.deliver(raw)
                except:
                    logger.warning('RPCReplyListener.callback: no RPC '
                                   + 'registered for message-id: [%s]' % id)
                break
        else:
            logger.warning('<rpc-reply> without message-id received: %s' % raw)
    
    def errback(self, err):
        logger.error('RPCReplyListener.errback: %r' % err)
        if self._errback is not None:
            self._errback(err)
