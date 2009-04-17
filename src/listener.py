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

class Subject:
    
    def __init__(self, listeners=[]):
        self._listeners = listeners
        
    def has_listener(self, listener):
        return (listener in self._listeners)
    
    def add_listner(self, listener):
            self._listeners.append(listener)

    def remove_listener(self, listener):
        self._listeners.remove(listener)

    def dispatch(self, event, *args, **kwds):
        try:
            func = getattr(Listener, event)
            for l in listeners:
                func(l, data)
        except AttributeError:
            pass

class Listener:
    
    @override
    def reply(self, *args, **kwds):
        raise NotImplementedError
    
    @override
    def error(self, *args, **kwds):
        raise NotImplementedError
