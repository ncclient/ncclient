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

import content

class SessionListener:

    def __init__(self):
        self._id2rpc = {}
        self._sub_id = None # message-id of <create-subscription> request
    
    def set_subscription(self, id):
        self._subscription = id
    
    def register(self, id, op):
        self._id2rpc[id] = op
    
    def unregister(self, id):
        del self._id2prc[id]
    
    ### Events
    
    def reply(self, raw):
        id = content.parse_message(raw)
        if id:
            self._id2rpc[id]._deliver(raw)
        else:
            self._id2rpc[self._sub_id]._notify(raw)
    
    def close(self, buf):
        pass # TODO
