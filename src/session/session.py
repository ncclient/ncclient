import Queue
import threading

class Session(threading.Thread):
    
    def __init__(self, capabilities):
        Thread.__init__()
        self._capabilities = capabilities
        self._id = None
        self._inQ = Queue.Queue() # server -> client
        self._outQ = Queue.Queue() # client -> server
        
    def connect(self):
        self.start()
        
    def run(self):
        raise NotImplementedError
        
    def send(self, msg):
        self._inQ.add(msg)

    def expect_close(self, val=True):
        '''operations.CloseSession must call this before a call to send(),
        so that the remote endpoint closing the connection does not result
        in an exception'''
        self._expect_close = val

    @property
    def id(self):
        'Session ID'
        return self._id
    
    @property
    def is_connected(self):
        return self._is_connected
    