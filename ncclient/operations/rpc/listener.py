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

from ncclient.glue import Listener
from ncclient.content import unqualify as __

import logging
logger = logging.getLogger('ncclient.rpc.listener')

class RPCReplyListener(Listener):
    
    # one instance per session
    def __new__(cls, session):
        instance = session.get_listener_instance(cls)
        if instance is None:
            instance = object.__new__(cls)
            instance._lock = Lock()
            instance._id2rpc = WeakValueDictionary()
            instance._pipelined = session.can_pipeline
            instance._errback = None
            session.add_listener(instance)
        return instance
    
    def register(self, id, rpc):
        with self._lock:
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
    
    def set_errback(self, errback):
        self._errback = errback
    
    def errback(self, err):
        if self._errback is not None:
            self._errback(err)
