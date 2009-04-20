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

import logging
import paramiko

from session import Session, SessionError

logger = logging.getLogger('ncclient.ssh')

class SessionCloseError(SessionError):
    
    def __str__(self):
        return 'RECEIVED: %s | UNSENT: %s' % (self._in_buf, self._out_buf)
    
    def __init__(self, in_buf, out_buf):
        SessionError.__init__(self)
        self._in_buf, self._out_buf = in_buf, out_buf

class SSHSession(Session):

    BUF_SIZE = 4096
    MSG_DELIM = ']]>]]>'
    
    def __init__(self, load_known_hosts=True,
                 missing_host_key_policy=paramiko.RejectPolicy):
        Session.__init__(self)
        self._in_buf = ''
        self._out_buf = ''
        self._client = paramiko.SSHClient()
        if load_known_hosts:
            self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(missing_host_key_policy)
    
    def load_host_keys(self, filename):
        self._client.load_host_keys(filename)
    
    def set_missing_host_key_policy(self, policy):
        self._client.set_missing_host_key_policy(policy)
    
    # paramiko exceptions ok?
    # user might be looking for ClientError
    def connect(self, hostname, port=830, username=None, password=None,
                key_filename=None, timeout=None, allow_agent=True,
                look_for_keys=True):
        self._client.connect(hostname, port=port, username=username,
                            password=password, key_filename=key_filename,
                            timeout=timeout, allow_agent=allow_agent,
                            look_for_keys=look_for_keys)    
        transport = self._client.get_transport()
        self._channel = transport.open_session()
        self._channel.invoke_subsystem('netconf')
        self._channel.set_name('netconf')
        self._connect()
    
    def run(self):
        
        chan = self._channel
        chan.setblocking(0)
        q = self._q
        
        while True:
            
            if chan.closed:
                break
            
            if chan.recv_ready():
                data = chan.recv(SSHSession.BUF_SIZE)
                if data:
                    self._in_buf += data
                    while True:
                        before, delim, after = self._in_buf.partition(SSHSession.MSG_DELIM)
                        if delim:
                            self.dispatch('reply', before)
                            self._in_buf = after
                        else:
                            break
                else:
                    break
            
            if chan.send_ready():
                if not q.empty():
                    msg = q.get()
                    self._out_buf += ( msg + SSHSession.MSG_DELIM )
                    while self._out_buf:
                        n = chan.send(self._out_buf)
                        if n <= 0:
                            break
                        self._out_buf = self._out_buf[n:]
        
        logger.debug('** broke out of main loop **')
        self.dispatch('close', SessionCloseError(self._in_buf, self._out_buf))
    
    def _close(self):
        self._channel.close()
        Session._close(self)


class MissingHostKeyPolicy(paramiko.MissingHostKeyPolicy):
    
    def __init__(self, cb):
        self._cb = cb
    
    def missing_host_key(self, client, hostname, key):
        if not self._cb(hostname, key):
            raise SSHError
