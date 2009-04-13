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

    @property
    def id(self):
        return self._id
    