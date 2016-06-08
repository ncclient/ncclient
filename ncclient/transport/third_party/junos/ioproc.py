import os
import sys
import re

if sys.version < '3':
    from cStringIO import StringIO
else:
    from io import StringIO
from select import select
from subprocess import Popen, check_output, PIPE, STDOUT

from ncclient.transport.errors import SessionCloseError, TransportError, PermissionError
from ncclient.transport.ssh import SSHSession

MSG_DELIM = "]]>]]>"
TICK = 0.1
NETCONF_SHELL = 'xml-mode netconf need-trailer'


class IOProc(SSHSession):

    def __init__(self, device_handler):
        SSHSession.__init__(self, device_handler)
        self._host_keys = None
        self._transport = None
        self._connected = False
        self._channel = None
        self._channel_id = None
        self._channel_name = None
        self._buffer = StringIO()  # for incoming data
        # parsing-related, see _parse()
        self._parsing_state = 0
        self._parsing_pos = 0
        self._device_handler = device_handler

    def close(self):
        self._channel.kill()
        self._connected = False

    def connect(self):
        stdoutdata = check_output(NETCONF_SHELL, shell=True, stdin=PIPE,
                                  stderr=STDOUT)
        if 'error: Restricted user session' in stdoutdata:
            obj = re.search(r'<error-message>\n?(.*)\n?</error-message>', stdoutdata, re.M)
            if obj:
                raise PermissionError(obj.group(1))
            else:
                raise PermissionError('Restricted user session')
        elif 'xml-mode: command not found' in stdoutdata:
            raise PermissionError('xml-mode: command not found')
        self._channel = Popen(NETCONF_SHELL, shell=True,
                              stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        self._connected = True
        self._channel_id = self._channel.pid
        self._channel_name = "netconf-shell"
        self._post_connect()
        return

    def run(self):
        chan = self._channel
        q = self._q
        try:
            while True:
                r, w, e = select([chan.stdout], [], [], TICK)
                data = []
                if r:
                    while True:
                        line = chan.stdout.readline()
                        data.append(line)
                        if MSG_DELIM in line:
                            break
                    if data:
                        self._buffer.write(b''.join(data))
                        self._parse()
                    else:
                        raise SessionCloseError(self._buffer.getvalue())
                if not q.empty():
                    data = q.get() + MSG_DELIM
                    while data:
                        chan.stdin.write(data)
                        chan.stdin.flush()
                        data = False
        except Exception as e:
            self.close()
            self._dispatch_error(e)

    @property
    def transport(self):
        "Underlying `paramiko.Transport <http://www.lag.net/paramiko/docs/paramiko.Transport-class.html>`_ object. This makes it possible to call methods like :meth:`~paramiko.Transport.set_keepalive` on it."
        return self._transport
