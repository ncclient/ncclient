import paramiko

from select import select as select

from session import Session

class SSH(Session):
    
    BUFSIZE = 4096
    
    def __init__(self, loadKnownHosts=True, hostname=None, port=22, authType=None, authInfo=None):
        Session.__init__(self)
        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        self._channel = None
        self._send_buffer
    
    def _connect(self):
        pass
    
    def _remote_closed(self):
        pass
    
    def _this_just_in(self, data):
        pass
    
    def connect(self):
        self._connect()
        self._channel = self._client.get_transport().open_session()
        self._channel.invoke_subsystem('netconf')
        Session.connect(self)
    
    def run(self):
        item = None
        sock = self._channel
        sock.setblocking(0)
        inQ, outQ = self._inQ, self._outQ
        while True:
            (r, w, e) = select([sock], [sock], [], 60)
            if w:
                if not outQ.empty():
                    to_send += outQ.get()
                if to_send:
                    to_send = to_send[sock.send(to_send):]
            if r:
                data = sock.recv(BUFSIZE)
                if data:
                    self._this_just_in(data)
                else:
                    self._remote_closed()                    
                    
class MissingHostKeyPolicy(paramiko.MissingHostKeyPolicy):
    pass
