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

from ncclient.rpc import RPC

class CloseSession(RPC):
    # tested: no
    # combed: yes
    
    SPEC = { 'tag': 'close-session' }
    
    def _delivery_hook(self):
        if self.reply.ok:
            self.session.expect_close()
        self.session.close()


class KillSession(RPC):
    # tested: no
    
    SPEC = {
        'tag': 'kill-session',
        'subtree': []
    }
    
    def request(self, session_id):
        spec = KillSession.SPEC.copy()
        if not isinstance(session_id, basestring): # just making sure...
            session_id = str(session_id)
        spec['subtree'].append({
            'tag': 'session-id',
            'text': session_id
        })
        return self._request(spec)
