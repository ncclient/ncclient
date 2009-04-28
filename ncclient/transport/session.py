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

from threading import Thread, Event

from ncclient.capabilities import Capabilities, CAPABILITIES
from ncclient.glue import Subject

from . import logger
from hello import HelloHandler

class Session(Thread, Subject):
    
    "TODO: docstring"
    
    def __init__(self):
        "TODO: docstring"
        Subject.__init__(self)
        Thread.__init__(self, name='session')
        self.setDaemon(True)
        self._client_capabilities = CAPABILITIES
        self._server_capabilities = None # yet
        self._id = None # session-id
        self._connected = False # to be set/cleared by subclass implementation
    
    def _post_connect(self):
        "TODO: docstring"
        self.send(HelloHandler.build(self._client_capabilities))
        error = None
        init_event = Event()
        # callbacks
        def ok_cb(id, capabilities):
            self._id, self._server_capabilities = id, Capabilities(capabilities)
            init_event.set()
        def err_cb(err):
            error = err
            init_event.set()
        listener = HelloHandler(ok_cb, err_cb)
        self.add_listener(listener)
        # start the subclass' main loop
        self.start()
        # we expect server's hello message
        init_event.wait()
        # received hello message or an error happened
        self.remove_listener(listener)
        if error:
            raise error
        logger.info('initialized: session-id=%s | server_capabilities=%s' %
                     (self.id, self.server_capabilities))
    
    def connect(self, *args, **kwds):
        "TODO: docstring"
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
    
    ### Properties
    
    @property
    def client_capabilities(self):
        return self._client_capabilities
    
    @property
    def server_capabilities(self):
        return self._server_capabilities
    
    @property
    def connected(self):
        return self._connected
    
    @property
    def id(self):
        return self._id
