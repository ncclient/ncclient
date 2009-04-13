import paramiko

from select import select as select

from session import Session

class SSH(Session):
    
    BUFSIZE = 4096
    
    DELIM = ']]>>]]>'
    
    def __init__(self, loadKnownHosts=True, hostname=None, port=22, authType=None, authInfo=None):
        Session.__init__(self)
        self._client = paramiko.SSHClient()
        if loadKnownHosts:
            self._client.load_system_host_keys()
        self._channel = None
        self._callback = None
        self._inBuf = ''
        self._outBuf = ''
    
    def _connect(self):
        self._callback = None #smthn
        self._outQ.add(hello)
    
    def _remote_closed(self):
        if not self._expectingClose:
            raise SomeException
    
    def _this_just_in(self, data):
        self._inBuf += data
        pos = self._inBuf.find(DELIM)
        if pos != -1:
            msg = self._inBuf[:pos]
            self._inBuf = self._inBuf[(pos + len(DELIM)):]
            self._callback(msg)
    
    def connect(self):
        self._connect()
        self._channel = self._client.get_transport().open_session()
        self._channel.invoke_subsystem('netconf')
        Session.connect(self)
    
    def run(self):
        sock = self._channel
        sock.setblocking(0)
        outQ = self._outQ
        while True:
            (r, w, e) = select([sock], [sock], [], 60)
            if w:
                if not outQ.empty():
                   self._outBuffer += ( outQ.get() + DELIM )
                if self._outBuffer:
                    n = sock.send(self._outBuffer)
                    self._outBuffer = self._outBuffer[n:]
            if r:
                data = sock.recv(BUFSIZE)
                if data:
                    self._this_just_in(data)
                else:
                    self._remote_closed()
                    
class MissingHostKeyPolicy(paramiko.MissingHostKeyPolicy): pass
