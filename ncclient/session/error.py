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

from ncclient import ClientError

class SessionError(ClientError):
    pass

class SSHError(SessionError):
    pass

class SSHUnknownHostError(SSHError):
    
    def __init__(self, hostname, key):
        self.hostname = hostname
        self.key = key
    
    def __str__(self):
        from binascii import hexlify
        return ('Unknown host key [%s] for [%s]' %
                (hexlify(self.key.get_fingerprint()), self.hostname))

class SSHAuthenticationError(SSHError):
    pass

class SSHSessionClosedError(SSHError):
    
    def __init__(self, in_buf, out_buf=None):
        SessionError.__init__(self, "Unexpected session close.")
        self._in_buf, self._out_buf = in_buf, out_buf
        
    def __str__(self):
        msg = SessionError(self).__str__()
        if self._in_buf:
            msg += '\nIN_BUFFER: %s' % self._in_buf
        if self._out_buf:
            msg += '\nOUT_BUFFER: %s' % self._out_buf
        return msg