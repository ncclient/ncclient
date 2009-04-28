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

from xml.etree import cElementTree as ET

from ncclient.glue import Listener
from ncclient.content import TreeBuilder, BASE_NS
from ncclient.content import qualify as _
from ncclient.content import unqualify as __

class HelloHandler(Listener):
    
    def __init__(self, init_cb, error_cb):
        self._init_cb, self._error_cb = init_cb, error_cb
    
    def __str__(self):
        return 'HelloListener'
    
    def callback(self, root, raw):
        if __(root[0]) == 'hello':
            try:
                id, capabilities = parse(raw)
            except Exception as e:
                self._error_cb(e)
            else:
                self._init_cb(id, capabilities)
    
    def errback(self, err):
        self._error_cb(err)
    
    @staticmethod
    def build(capabilities, encoding='utf-8'):
        "Given a list of capability URI's returns encoded <hello> message"
        spec = {
            'tag': _('hello', BASE_NS),
            'children': [{
                'tag': 'capabilities',
                'children': # this is fun :-)
                    [{ 'tag': 'capability', 'text': uri} for uri in capabilities]
                }]
            }
        return TreeBuilder(spec).to_string(encoding)
    
    @staticmethod
    def parse(raw):
        "Returns tuple of ('session-id', ['capability_uri', ...])"
        sid, capabilities = 0, []
        root = ET.fromstring(raw)
        for child in root.getchildren():
            if __(child.tag) == 'session-id':
                sid = child.text
            elif __(child.tag) == 'capabilities':
                for cap in child.getiterator(_('capability', BASE_NS)):
                    capabilities.append(cap.text)
                # cisco doesn't namespace hello message
                for cap in child.getiterator('capability'): 
                    capabilities.append(cap.text)
        return sid, capabilities
