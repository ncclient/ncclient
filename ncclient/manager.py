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


def connect_ssh(*args, **kwds):
    session = transport.SSHSession(capabilities.CAPABILITIES)
    session.load_system_host_keys()
    session.connect(*args, **kwds)
    return Manager(session)

connect = connect_ssh # default session type

RAISE_ALL, RAISE_ERROR, RAISE_NONE = range(3)

class Manager:
    
    "Thin layer of abstraction for the API."
    
    def __init__(self, session, rpc_error=RAISE_ALL):
        self._session = session
        self._raise = rpc_error

    def do(self, op, *args, **kwds):
        op = operations.OPERATIONS[op](self._session)
        reply = op.request(*args, **kwds)
        if not reply.ok:
            if self._raise == RAISE_ALL:
                raise reply.error
            elif self._raise == RAISE_ERROR:
                for error in reply.errors:
                    if error.severity == 'error':
                        raise error
        return reply
    
    def __enter__(self):
        pass
    
    def __exit__(self, *args):
        self.close()
        return False
    
    def locked(self, target):
        """Returns a context manager for use withthe 'with' statement.
        `target` is the datastore to lock, e.g. 'candidate
        """
        return operations.LockContext(self._session, target)
     
    get = lambda self, *args, **kwds: self.do('get', *args, **kwds).data
    
    get_config = lambda self, *args, **kwds: self.do('get-config', *args, **kwds).data
    
    edit_config = lambda self, *args, **kwds: self.do('edit-config', *args, **kwds)
    
    copy_config = lambda self, *args, **kwds: self.do('copy-config', *args, **kwds)
    
    validate = lambda self, *args, **kwds: self.do('validate', *args, **kwds)
    
    commit = lambda self, *args, **kwds: self.do('commit', *args, **kwds)
    
    discard_changes = lambda self, *args, **kwds: self.do('discard-changes', *args, **kwds)
    
    delete_config = lambda self, *args, **kwds: self.do('delete-config', *args, **kwds)
    
    lock = lambda self, *args, **kwds: self.do('lock', *args, **kwds)
    
    unlock = lambda self, *args, **kwds: self.do('unlock', *args, **kwds)
    
    close_session = lambda self, *args, **kwds: self.do('close-session', *args, **kwds)
    
    kill_session = lambda self, *args, **kwds: self.do('kill-session', *args, **kwds)
    
    def close(self):
        try: # try doing it clean
            self.close_session()
        except:
            pass
        if self._session.connected: # if that didn't work...
            self._session.close()
    
    @property
    def session(self, session):
        return self._session
    
    def get_capabilities(self, whose):
        if whose in ('manager', 'client'):
            return self._session._client_capabilities
        elif whose in ('agent', 'server'):
            return self._session._server_capabilities
    
    @property
    def capabilities(self):
        return self._session._client_capabilities
