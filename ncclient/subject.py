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

import logging

logger = logging.getLogger('ncclient.subject')

class Subject:
        
    def __init__(self, listeners=[]):
        self._listeners = set(listeners)
        self._lock = Lock()
    
    def has_listener(self, listener):
        with self._lock:
            return (listener in self._listeners)
    
    def add_listener(self, listener):
        with self._lock:
            self._listeners.add(listener)
    
    def remove_listener(self, listener):
        with self._lock:
            self._listeners.discard(listener)
    
    def dispatch(self, event, *args, **kwds):
        # holding the lock while doing callbacks could lead to a deadlock
        # if one of the above methods is called
        with self._lock:
            listeners = list(self._listeners)
        for l in listeners:
            try:
                logger.debug('dispatching [%s] to [%s]' % (event, l))
                getattr(l, event)(*args, **kwds)
            except Exception as e:
                logger.warning(e)
