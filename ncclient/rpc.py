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

from listener import SessionListener

from uuid import uuid1

class RPC:
    
    def __init__(self, session, async=False):
        self._session = session
        self._async = async
        self._reply = None
        self._reply_event = Event()
        self._id = uuid1().urn

    def _listener(self):
        if not RPC.listeners.has_key(self._session.id):
            RPC.listeners[self._session.id] = SessionListener()
        return RPC.listeners[self._session.id]

    def request(self, async=False):
        self._async = async
        listener = SessionListener(self._session.id)
        session.add_listener(listener)
        listener.register(self._id, self)
        self._session.send(self.to_xml())
    
    def response_cb(self, reply):
        self._reply = reply # does callback parse??
        self._event.set()
    
    @property
    def has_reply(self):
        return self._reply_event.isSet()
    
    def wait_on_reply(self, timeout=None):
        self._reply_event.wait(timeout)
    
    @property
    def is_async(self):
        return self._async
    
    @property
    def id(self):
        return self._id