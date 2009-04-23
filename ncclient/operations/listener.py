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

from weakref import WeakValueDictionary

from ncclient.content.parsers import RootParser

_listeners = WeakValueDictionary()

def get_listener(session):
    try:
        return _listeners[session]
    except KeyError:
        _listeners[session] = MessageListener()
        return _listeners[session]

class MessageListener:
    
    def __init__(self):
        # {message-id: RPC}
        self._rpc = WeakValueDictionary()
        # if the session gets closed by remote endpoint,
        # need to know if it is an error event or was requested through
        # a NETCONF operation i.e. CloseSession
        self._expecting_close = False
        # other recognized names and behavior on receiving them
        self._recognized = []
    
    def __str__(self):
        return 'MessageListener'
    
    def expect_close(self):
        self._expecting_close = True
    
    def register(self, id, op):
        self._id2rpc[id] = op
    
    ### Events
    
    def reply(self, raw):
        pass
    
    def error(self, err):
        from ncclient.session.session import SessionCloseError
        if err is SessionCloseError:
            logger.debug('session closed by remote endpoint, expecting_close=%s' %
                         self._expecting_close)
            if not self._expecting_close:
                raise err
