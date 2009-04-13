class Message:
    
    def __init__(self, id, content):
        self.id = id
        self.content = content

class IncomingMessage(Message):
    
    def __init__(self, id, content, ):
        Message.__init__(id, content)

class OutgoingMessage(Message):
    
    def __init__(self, id, content, replyCallback=None, isCloseMessage=False):
        Message.__init__(id, content)
        self.replyCallback = replyCallback
        self.isCloseMessage = isCloseMessage

class MessageIDProvider:
    
    def __init__(self):
        self.curID = 1
            
    @property
    def nextID(self):
        self.curID += 1
        return self.curID
