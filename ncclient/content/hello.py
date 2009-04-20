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

import logging
from xml.etree import cElementTree as ElementTree

logging.getLogger('ncclient.content.hello')

from ..capability import Capabilities

ns = 'urn:ietf:params:xml:ns:netconf:base:1.0'

def make(capabilities):
    return '<hello xmlns="%s">%s</hello>' % (ns, capabilities)

def parse(raw):
    id, capabilities = 0, Capabilities()
    hello = ElementTree.fromstring(raw)
    for child in hello.getchildren():
        if child.tag == '{%s}session-id' % ns:
            id = child.text
        elif child.tag == '{%s}capabilities' % ns:
            for cap in child.getiterator('{%s}capability' % ns):
                capabilities.add(cap.text)
    return id, capabilities

#class HelloParser:
#    
#    'Fast parsing with expat'
#    
#    capability, sid = range(2)
#    
#    def __init__(self, raw):
#        self._sid = None
#        self._capabilities = Capabilities()
#        p = xml.parsers.expat.ParserCreate()
#        p.StartElementHandler = self._start_element
#        p.EndElementHandler = self._end_element
#        p.CharacterDataHandler = self._char_data
#        self._expect = None
#        p.parse(raw, True)
#    
#    def _start_element(self, name, attrs):
#        if name == 'capability':
#            self._expect = HelloParser.capability
#        elif name == 'session-id':
#            self._expect = HelloParser.sid
#    
#    def _end_element(self, name):
#        self._expect = None
#    
#    def _char_data(self, data):
#        if self._expect == HelloParser.capability:
#            self._capabilities.add(data)
#        elif self._expect == HelloParser.sid:
#            self._sid = int(data)
#    
#    @property
#    def sid(self): return self._sid
#    
#    @property
#    def capabilities(self): return self._capabilities