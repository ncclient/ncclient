import paramiko

from session import Session

class SSH(Session):
    
    def __init__(self, loadKnownHosts=True, hostname=None, port=22, authType=None, authInfo=None):
        Session.__init__(self)
        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        self._channel = None
        self._send_buffer
    
    def _connect(self):
        pass
    
    def connect(self):
        self._connect()
        self._channel = self._client.get_transport().get_channel()
        self._channel.invoke_subsystem('netconf')
        Session.connect(self)
    
    def run(self):
        item = None
        sock = self._channel
        inQ, outQ = self._inQ, self._outQ
        while True:
            if not self._outQ.empty():
                sock.send(s)
            self._send(self)
            self._recv(self)
    
class MissingHostKeyPolicy(paramiko.MissingHostKeyPolicy):
    pass
