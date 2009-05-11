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

"All to do with NETCONF <hello> messages"

from ncclient import content

class HelloHandler(Listener):
    
    def __init__(self, init_cb, error_cb):
        self._init_cb = init_cb
        self._error_cb = error_cb
    
    def __str__(self):
        return 'HelloListener'
    
    def callback(self, root, raw):
        if content.unqualify(root[0]) == 'hello':
            try:
                id, capabilities = HelloHandler.parse(raw)
            except Exception as e:
                self._error_cb(e)
            else:
                self._init_cb(id, capabilities)
    
    def errback(self, err):
        self._error_cb(err)
    
    @staticmethod
    def build(capabilities):
        "Given a list of capability URI's returns encoded <hello> message"
        spec = {
            'tag': content.qualify('hello'),
            'children': [{
                'tag': 'capabilities',
                'children': # this is fun :-)
                    [{ 'tag': 'capability', 'text': uri} for uri in capabilities]
                }]
            }
        return content.to_xml(spec)
    
    @staticmethod
    def parse(raw):
        "Returns tuple of ('session-id', ['capability_uri', ...])"
        sid, capabilities = 0, []
        root = content.from_xml(raw)
        for child in root['children']:
            tag = content.unqualify(child['tag'])
            if tag == 'session-id':
                sid = child['text']
            elif tag == 'capabilities':
                for cap in child['children']:
                    if content.unqualify(cap['text']) == 'capability':
                        capabilities.append(cap['text'])
        return sid, capabilities
