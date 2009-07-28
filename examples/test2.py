from ncclient.transport import SSHSession
from ncclient.operations import CloseSession
from ncclient.capabilities import CAPABILITIES
from ncclient import operations

import logging
logging.basicConfig(level=logging.DEBUG)

from ncclient.operations.rpc import RPC
class FakeOp(RPC):
    def request(self):
        return self._request({'tag': 'fake-operation'})

s = SSHSession(CAPABILITIES)
#s.add_listener(PrintListener())
s.load_known_hosts()
s.connect('broccoli', 22, username='sbhushan')

fo = FakeOp(s)
fo_reply = fo.request()
if not fo_reply.ok:
    print 'error dictionary: %r' % fo_reply.error
else:
    print 'fake op went ok?!'
    print fo_reply

go = operations.Get(s)
go.request()
print 'GET_REPLY', go.reply.data_xml

cs = CloseSession(s)
cs_reply = cs.request()
print 'closesession ok:', cs_reply.ok
