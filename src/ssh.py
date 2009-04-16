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

from select import select as select

from session import Session, SessionError

logger = logging.getLogger('ncclient.ssh')

class SSHError(SessionError): pass

class SSHSession(Session):
    
    BUF_SIZE = 4096
    
    MSG_DELIM = ']]>>]]>'
    
    def __init__(self, capabilities, reply_cb=None,
                 load_known_hosts=True,
                 missing_host_key_policy=paramiko.RejectPolicy):
        Session.__init__(self, capabilities)
        self._inBuf = ''
        self._outBuf = ''
        self._client = SSHClient()
        if load_known_hosts:
            self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(host_key_policy)
        
    def _greet_cb(self, reply):
        self._init(reply)
        self._cb = self._real_cb
        
    def _greet(self):
        self._real_cb = self._cb
        self._cb = self._greet_cb
        self._q.add(self._make_hello())
        
    def load_host_keys(self, filename):
        self._client.load_host_keys(filename)
        
    def set_missing_host_key_policy(self, policy):
        self._client.set_missing_host_key_policy(policy)
        
    def set_reply_callback(self, cb):
        self._cb = cb
    
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
        self._greet()
        Session.connect(self) # starts thread
    
    def run(self):
        sock = self._channel
        sock.setblocking(0)
        q = self._q
        while True:
            (r, w, e) = select([sock], [sock], [], 60)
            if w:
                if not q.empty():
                   self._outBuffer += ( q.get() + MSG_DELIM )
                if self._outBuffer:
                    n = sock.send(self._outBuffer)
                    self._outBuffer = self._outBuffer[n:]
            if r:
                data = sock.recv(BUF_SIZE)
                if data:
                    self._inBuf += data
                    # probably not very efficient:
                    pos = self._inBuf.find(DELIM)
                    if pos != -1:
                        msg = self._inBuf[:pos]
                        self._inBuf = self._inBuf[(pos + len(DELIM)):]
                        self._reply_cb(msg)
                else:
                    connected = False
                    # it's not an error if we asked for it
                    # via CloseSession -- need a way to know this
                    raise SessionError
                    
class CallbackPolicy(paramiko.MissingHostKeyPolicy):
    
    def __init__(self, cb):
        self._cb = cb
    
    def missing_host_key(self, client, hostname, key):
        if not self._cb(hostname, key):
            raise SSHError
