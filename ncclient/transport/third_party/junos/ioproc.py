import os
from select import select
from subprocess import Popen, PIPE, STDOUT

from ncclient import compat
from ncclient.transport.errors import SessionCloseError, TransportError
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
        self._buffer = compat.StringIO()  # for incoming data
        # parsing-related, see _parse()
        self._parsing_state = 0
        self._parsing_pos = 0
        self._device_handler = device_handler

    def close(self):
        self._channel.kill()
        self._connected = False

    def connect(self):

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
                data = ''
                if r:
                    while True:
                        data += chan.stdout.readline()
                        if MSG_DELIM in data:
                            break
                    if data:
                        self._buffer.write(data)
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
