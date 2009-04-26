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

import os
import socket
from binascii import hexlify
from cStringIO import StringIO
from select import select

import paramiko

from . import logger
from errors import SSHError, SSHUnknownHostError, SSHAuthenticationError, SessionCloseError
from session import Session

BUF_SIZE = 4096
MSG_DELIM = ']]>]]>'
TICK = 0.1

class SSHSession(Session):

    def __init__(self):
        Session.__init__(self)
        self._host_keys = paramiko.HostKeys()
        self._system_host_keys = paramiko.HostKeys()
        self._transport = None
        self._connected = False
        self._channel = None
        self._buffer = StringIO() # for incoming data
        # parsing-related, see _parse()
        self._parsing_state = 0 
        self._parsing_pos = 0
    
    def _parse(self):
        '''Messages ae delimited by MSG_DELIM. The buffer could have grown by a
        maximum of BUF_SIZE bytes everytime this method is called. Retains state
        across method calls and if a byte has been read it will not be considered
        again.
        '''
        delim = MSG_DELIM
        n = len(delim) - 1
        expect = self._parsing_state
        buf = self._buffer
        buf.seek(self._parsing_pos)
        while True:
            x = buf.read(1)
            if not x: # done reading
                break
            elif x == delim[expect]: # what we expected
                expect += 1 # expect the next delim char
            else:
                continue
            # loop till last delim char expected, break if other char encountered
            for i in range(expect, n):
                x = buf.read(1)
                if not x: # done reading
                    break
                if x == delim[expect]: # what we expected
                    expect += 1 # expect the next delim char
                else:
                    expect = 0 # reset
                    break
            else: # if we didn't break out of the loop, full delim was parsed
                msg_till = buf.tell() - n
                buf.seek(0)
                msg = buf.read(msg_till)
                self.dispatch('received', msg)
                buf.seek(n+1, os.SEEK_CUR)
                rest = buf.read()
                buf = StringIO()
                buf.write(rest)
                buf.seek(0)
                expect = 0
        self._buffer = buf
        self._parsing_state = expect
        self._parsing_pos = self._buffer.tell()
    
    def load_system_host_keys(self, filename=None):
        if filename is None:
            filename = os.path.expanduser('~/.ssh/known_hosts')
            try:
                self._system_host_keys.load(filename)
            except IOError:
                # for windows
                filename = os.path.expanduser('~/ssh/known_hosts')
                try:
                    self._system_host_keys.load(filename)
                except IOError:
                    pass
            return
        self._system_host_keys.load(filename)
    
    def load_host_keys(self, filename):
        self._host_keys.load(filename)

    def add_host_key(self, key):
        self._host_keys.add(key)
    
    def save_host_keys(self, filename):
        f = open(filename, 'w')
        for hostname, keys in self._host_keys.iteritems():
            for keytype, key in keys.iteritems():
                f.write('%s %s %s\n' % (hostname, keytype, key.get_base64()))
        f.close()    
    
    def close(self):
        if self._transport.is_active():
            self._transport.close()
        self._connected = False
    
    def connect(self, hostname, port=830, timeout=None,
                unknown_host_cb=None, username=None, password=None,
                key_filename=None, allow_agent=True, look_for_keys=True):
        
        assert(username is not None)
        
        for (family, socktype, proto, canonname, sockaddr) in \
        socket.getaddrinfo(hostname, port):
            if socktype==socket.SOCK_STREAM:
                af = family
                addr = sockaddr
                break
        else:
            raise SSHError('No suitable address family for %s' % hostname)
        sock = socket.socket(af, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(addr)
        t = self._transport = paramiko.Transport(sock)
        t.set_log_channel(logger.name)
        
        try:
            t.start_client()
        except paramiko.SSHException:
            raise SSHError('Negotiation failed')
        
        # host key verification
        server_key = t.get_remote_server_key()
        known_host = self._host_keys.check(hostname, server_key) or \
                        self._system_host_keys.check(hostname, server_key)
        
        if unknown_host_cb is None:
            unknown_host_cb = lambda *args: False
        if not known_host and not unknown_host_cb(hostname, server_key):
                raise SSHUnknownHostError(hostname, server_key)
        
        if key_filename is None:
            key_filenames = []
        elif isinstance(key_filename, basestring):
            key_filenames = [ key_filename ]
        else:
            key_filenames = key_filename
        
        self._auth(username, password, key_filenames, allow_agent, look_for_keys)
        
        self._connected = True # there was no error authenticating
        
        c = self._channel = self._transport.open_session()
        c.invoke_subsystem('netconf')
        c.set_name('netconf')
        
        self._post_connect()
    
    # on the lines of paramiko.SSHClient._auth()
    def _auth(self, username, password, key_filenames, allow_agent,
              look_for_keys):
        saved_exception = None
        
        for key_filename in key_filenames:
            for cls in (paramiko.RSAKey, paramiko.DSSKey):
                try:
                    key = cls.from_private_key_file(key_filename, password)
                    logger.debug('Trying key %s from %s' %
                              (hexlify(key.get_fingerprint()), key_filename))
                    self._transport.auth_publickey(username, key)
                    return
                except Exception as e:
                    saved_exception = e
                    logger.debug(e)
        
        if allow_agent:
            for key in paramiko.Agent().get_keys():
                try:
                    logger.debug('Trying SSH agent key %s' %
                                 hexlify(key.get_fingerprint()))
                    self._transport.auth_publickey(username, key)
                    return
                except Exception as e:
                    saved_exception = e
                    logger.debug(e)
        
        keyfiles = []
        if look_for_keys:
            rsa_key = os.path.expanduser('~/.ssh/id_rsa')
            dsa_key = os.path.expanduser('~/.ssh/id_dsa')
            if os.path.isfile(rsa_key):
                keyfiles.append((paramiko.RSAKey, rsa_key))
            if os.path.isfile(dsa_key):
                keyfiles.append((paramiko.DSSKey, dsa_key))
            # look in ~/ssh/ for windows users:
            rsa_key = os.path.expanduser('~/ssh/id_rsa')
            dsa_key = os.path.expanduser('~/ssh/id_dsa')
            if os.path.isfile(rsa_key):
                keyfiles.append((paramiko.RSAKey, rsa_key))
            if os.path.isfile(dsa_key):
                keyfiles.append((paramiko.DSSKey, dsa_key))
        
        for cls, filename in keyfiles:
            try:
                key = cls.from_private_key_file(filename, password)
                logger.debug('Trying discovered key %s in %s' %
                          (hexlify(key.get_fingerprint()), filename))
                self._transport.auth_publickey(username, key)
                return
            except Exception as e:
                saved_exception = e
                logger.debug(e)
        
        if password is not None:
            try:
                self._transport.auth_password(username, password)
                return
            except Exception as e:
                saved_exception = e
                logger.debug(e)
        
        if saved_exception is not None:
            raise SSHAuthenticationError(repr(saved_exception))
        
        raise SSHAuthenticationError('No authentication methods available')
    
    def run(self):
        chan = self._channel
        chan.setblocking(0)
        q = self._q
        try:
            while True:
                # select on a paramiko ssh channel object does not ever return
                # it in the writable list, so it channel's don't exactly emulate 
                # the socket api
                r, w, e = select([chan], [], [], TICK)
                # will wakeup evey TICK seconds to check if something
                # to send, more if something to read (due to select returning
                # chan in readable list)
                if r:
                    data = chan.recv(BUF_SIZE)
                    if data:
                        self._buffer.write(data)
                        self._parse()
                    else:
                        raise SessionCloseError(self._buffer.getvalue())
                if not q.empty() and chan.send_ready():
                    data = q.get() + MSG_DELIM
                    while data:
                        n = chan.send(data)
                        if n <= 0:
                            raise SessionCloseError(self._buffer.getvalue(), data)
                        data = data[n:]
        except Exception as e:
            self.close()
            logger.debug('*** broke out of main loop ***')
            self.dispatch('error', e)
    
    @property
    def transport(self):
        '''Get underlying paramiko.transport object; this is provided so methods
        like transport.set_keepalive can be called.
        '''
        return self._transport
