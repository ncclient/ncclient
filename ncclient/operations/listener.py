#!/usr/bin/env python

_listeners = WeakValueDictionary()

def get_listener(session):
    try:
        return _listeners[session]
    except KeyError:
        _listeners[session] = MessageListener()
        return _listeners[session]

class MessageListener:
    
    def __init__(self):
        # {message-id: RPC}
        self._rpc = WeakValueDictionary()
        # if the session gets closed by remote endpoint,
        # need to know if it is an error event or was requested through
        # a NETCONF operation i.e. CloseSession
        self._expecting_close = False
        # other recognized names and behavior on receiving them
        self._recognized = []
    
    def __str__(self):
        return 'MessageListener'
    
    def expect_close(self):
        self._expecting_close = True
    
    def register(self, id, op):
        self._id2rpc[id] = op
    
    ### Events
    
    def reply(self, raw):
        pass
    
    def error(self, err):
        from ncclient.session.session import SessionCloseError
        if err is SessionCloseError:
            logger.debug('session closed by remote endpoint, expecting_close=%s' %
                         self._expecting_close)
            if not self._expecting_close:
                raise err
