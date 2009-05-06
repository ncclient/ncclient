# Copyright 2009 Shikhar Bhushan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# TODO when can actually test it...

from ncclient.rpc import RPC

from ncclient.glue import Listener
from ncclient.content import qualify as _

NOTIFICATION_NS = 'urn:ietf:params:xml:ns:netconf:notification:1.0'

class CreateSubscription(RPC):    
    
    SPEC = {
        'tag': _('create-subscription', NOTIFICATION_NS),
        'startTime': None,
        'stream': None
    }

class Notification:
    pass

class NotificationListener(Listener):
    pass
