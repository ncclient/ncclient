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
from operations import OPERATIONS
import transport


def ssh_connect(*args, **kwds):
    session = transport.SSHSession(capabilities.CAPABILITIES)
    session.load_system_host_keys()
    session.connect(*args, **kwds)
    return Manager(session)

connect = ssh_connect # default session type

#: Raise all errors
RAISE_ALL = 0
#:
RAISE_ERR = 1
#:
RAISE_NONE = 2

class Manager:

    "Thin layer of abstraction for the ncclient API."

    def __init__(self, session):
        self._session = session
        self._rpc_error_action = RAISE_ALL

    def set_rpc_error_action(self, action):
        self._rpc_error_handling = option

    def do(self, op, *args, **kwds):
        op = OPERATIONS[op](self._session)
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
        """Returns a context manager for use with the 'with' statement.

        :arg target: name of the datastore to lock
        :type target: `string`
        """
        return operations.LockContext(self._session, target)

    def get(self, filter=None):
        pass

    def get_config(self, source, filter=None):
        pass

    def copy_config(self, source, target):
        pass

    def validate(self, source):
        pass

    def commit(self, target):
        pass

    def discard_changes(self):
        pass

    def delete_config(self, target):
        pass

    def lock(self, target):
        pass

    def unlock(self, target):
        pass

    def close_session(self):
        pass

    def kill_session(self, session_id):
        pass

    def confirmed_commit(self, timeout=None):
        pass

    def confirm(self):
        # give confirmation
        pass

    def discard_changes(self):
        pass

    lock = lambda self, *args, **kwds: self.do('lock', *args, **kwds)

    unlock = lambda self, *args, **kwds: self.do('unlock', *args, **kwds)

    close_session = lambda self, *args, **kwds: self.do('close-session', *args, **kwds)

    kill_session = lambda self, *args, **kwds: self.do('kill-session', *args, **kwds)

    def close(self):
        try: # try doing it clean
            self.close_session()
        except Exception as e:
            logger.debug('error doing <close-session> -- %r' % e)
        if self._session.connected: # if that didn't work...
            self._session.close()

    @property
    def session(self, session):
        return self._session

    @property
    def client_capabilities(self):
        return self._session._client_capabilities

    @property
    def server_capabilities(self):
        return self._session._server_capabilities

    @property
    def session_id(self):
        return self._session.id
