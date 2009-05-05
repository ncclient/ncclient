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

import capabilities
import operations
import transport

SESSION_TYPES = {
    'ssh': transport.SSHSession
}

OPERATIONS = {
    'get': operations.Get,
    'get-config': operations.GetConfig,
    'edit-config': operations.EditConfig,
    'copy-config': operations.CopyConfig,
    'validate': operations.Validate,
    'commit': operations.Commit,
    'discard-changes': operations.DiscardChanges,
    'delete-config': operations.DeleteConfig,
    'lock': operations.Lock,
    'unlock': operations.Unlock,
    'close_session': operations.CloseSession,
    'kill-session': operations.KillSession,
}

class Manager(type):
    
    'Facade for the API'
    
    def connect(self, session_type, *args, **kwds):
        self._session = SESSION_TYPES[session_type](capabilities.CAPABILITIES)
        self._session.connect(*args, **kwds)
    
    def __getattr__(self, name):
        if name in OPERATIONS:
            return OPERATIONS[name](self._session).request
        else:
            raise AttributeError
