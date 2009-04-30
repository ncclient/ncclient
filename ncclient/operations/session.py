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

'Session-related NETCONF operations'

from rpc import RPC
from copy import deepcopy

class CloseSession(RPC):
    
    'CloseSession is always synchronous'
    
    SPEC = { 'tag': 'close-session' }
    
    def _delivery_hook(self):
        if self.reply.ok:
            self.session.expect_close()
        self.session.close()
    
    def request(self):
        return self._request(CloseSession.SPEC)


class KillSession(RPC):
    
    SPEC = {
        'tag': 'kill-session',
        'children': [ { 'tag': 'session-id', 'text': None} ]
    }
    
    def request(self, session_id):
        if not isinstance(session_id, basestring): # just making sure...
            session_id = str(session_id)
        spec = deepcopy(SPEC)
        spec['children'][0]['text'] = session_id
        return self._request(spec)
