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

from os import SEEK_CUR
from cStringIO import StringIO

from session import Session, SessionError

logger = logging.getLogger('ncclient.ssh')


class SessionCloseError(SessionError):
    
    def __str__(self):
        return 'RECEIVED: %s | UNSENT: %s' % (self._in_buf, self._out_buf)
    
    def __init__(self, in_buf, out_buf=None):
        SessionError.__init__(self)
        self._in_buf, self._out_buf = in_buf, out_buf


class SSHSession(Session):

    BUF_SIZE = 4096
    MSG_DELIM = ']]>]]>'
    
    def __init__(self, load_known_hosts=True,
                 missing_host_key_policy=paramiko.RejectPolicy):
        Session.__init__(self)
        self._client = paramiko.SSHClient()
        if load_known_hosts:
            self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(missing_host_key_policy)
        self._in_buf = StringIO()
        self._parsing_state = 0
        self._parsing_pos = 0
    
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
        self._connected = True
        self._post_connect()
    
    def run(self):
        chan = self._channel
        chan.setblocking(0)
        q = self._q
        bufsize = SSHSession.BUF_SIZE
        delim = SSHSession.MSG_DELIM
        try:
            while True:    
                if chan.closed:
                    raise SessionCloseError(self._in_buf.getvalue())         
                if chan.send_ready() and not q.empty():
                    data = q.get() + delim
                    while data:
                        n = chan.send(data)
                        if n <= 0:
                            raise SessionCloseError(self._in_buf.getvalue(), data)
                        data = data[n:]
                if chan.recv_ready():
                    data = chan.recv(bufsize)
                    if data:
                        self._in_buf.write(data)
                        self._parse()
                    else:
                        raise SessionCloseError(self._in_buf.getvalue())
        except Exception as e:
            logger.debug('*** broke out of main loop ***')
            self.dispatch('error', e)
    
    def _close(self):
        self._channel.close()
        self._connected = False
    
    def _parse(self):
        delim = SSHSession.MSG_DELIM
        n = len(delim) - 1
        state = self._parsing_state
        buf = self._in_buf
        buf.seek(self._parsing_pos)
        while True:
            x = buf.read(1)
            if not x: # done reading
                break
            elif x == delim[state]:
                state += 1
            else:
                continue
            # loop till last delim char expected, break if other char encountered
            for i in range(state, n):
                x = buf.read(1)
                if not x: # done reading
                    break
                if x==delim[i]: # what we expected
                    state += 1 # expect the next delim char
                else:
                    state = 0 # reset
                    break
            else: # if we didn't break out of above loop, full delim parsed
                till = buf.tell() - n
                buf.seek(0)
                msg = buf.read(till)
                self.dispatch('reply', msg)
                buf.seek(n+1, SEEK_CUR)
                rest = buf.read()
                buf = StringIO()
                buf.write(rest)
                buf.seek(0)
                state = 0
        self._in_buf = buf
        self._parsing_state = state
        self._parsing_pos = self._in_buf.tell()

class MissingHostKeyPolicy(paramiko.MissingHostKeyPolicy):
    
    def __init__(self, cb):
        self._cb = cb
    
    def missing_host_key(self, client, hostname, key):
        if not self._cb(hostname, key):
            raise SSHError
