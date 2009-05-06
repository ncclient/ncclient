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

def connect_ssh(*args, **kwds):
    session = transport.SSHSession(capabilities.CAPABILITIES)
    session.load_system_host_keys()
    session.connect(*args, **kwds)
    return Manager(session)

connect = connect_ssh # default

class Manager:
    
    'Facade for the API'
    
    def __init__(self, session):
        self._session = session
    
    def _get(self, type, *args, **kwds):
        op = OPERATIONS[type](self._session)
        reply = op.request(*args, **kwds)
        if not reply.ok:
            raise reply.errors[0]
        else:
            return reply.data

    def request(op, *args, **kwds):
        op = OPERATIONS[op](self._session)
        reply = op.request(*args, **kwds)
        if not reply.ok:
            raise reply.errors[0]
        return reply

    def locked(self, target='running'):
        return LockContext(self._session, target)
    
    get = lambda self, *args, **kwds: self._get('get')
    
    get_config = lambda self, *args, **kwds: self._get('get-config')
    
    edit_config = lambda self, *args, **kwds: self.request('edit-config', *args, **kwds)
    
    copy_config = lambda self, *args, **kwds: self.request('copy-config', *args, **kwds)
    
    validate = lambda self, *args, **kwds: self.request('validate', *args, **kwds)
    
    commit = lambda self, *args, **kwds: self.request('commit', *args, **kwds)
    
    discard_changes = lambda self, *args, **kwds: self.request('discard-changes', *args, **kwds)
    
    delete_config = lambda self, *args, **kwds: self.request('delete-config', *args, **kwds)
    
    lock = lambda self, *args, **kwds: self.request('lock', *args, **kwds)
    
    unlock = lambda self, *args, **kwds: self.request('unlock', *args, **kwds)
    
    close_session = lambda self, *args, **kwds: self.request('close-session', *args, **kwds)
    
    kill_session = lambda self, *args, **kwds: self.request('kill-session', *args, **kwds)
    
    def close(self):
        try:
            self.close_session()
        except:
            self._session.expect_close()
            self._session.close()
