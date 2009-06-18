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

from copy import deepcopy

from rpc import RPC

class CloseSession(RPC):

    "*<close-session>* RPC. The connection to NETCONF server is also closed."

    SPEC = { 'tag': 'close-session' }

    def request(self):
        try:
            return self._request(CloseSession.SPEC)
        finally:
            self.session.close()


class KillSession(RPC):

    "*<kill-session>* RPC."

    SPEC = {
        'tag': 'kill-session',
        'subtree': []
    }

    def request(self, session_id):
        """
        :arg session_id: *session-id* of NETCONF session to kill
        :type session_id: `string`

        :seealso: :ref:`return`
        """
        spec = deepcopy(KillSession.SPEC)
        if not isinstance(session_id, basestring): # make sure
            session_id = str(session_id)
        spec['subtree'].append({
            'tag': 'session-id',
            'text': session_id
        })
        return self._request(spec)
