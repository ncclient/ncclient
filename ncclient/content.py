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

NAMESPACE = 'urn:ietf:params:xml:ns:netconf:base:1.0'

def qualify(tag, ns=NAMESPACE):
    return '{%s}%s' % (ns, tag)

_ = qualify

def make_hello(capabilities):
    return '<hello xmlns="%s">%s</hello>' % (NAMESPACE, capabilities)

def make_rpc(id, op):
    return '<rpc message-id="%s" xmlns="%s">%s</rpc>' % (id, NAMESPACE, op)

def parse_hello(raw):
    from capability import Capabilities
    id, capabilities = 0, Capabilities()
    root = ElementTree.fromstring(raw)
    if root.tag == _('hello'):
        for child in hello.getchildren():
            if child.tag == _('session-id'):
                id = int(child.text)
            elif child.tag == _('capabilities'):
                for cap in child.getiterator(_('capability')):
                    capabilities.add(cap.text)
    return id, capabilities

def parse_message_type(raw):
    'returns 0 if notification, message-id if rpc-reply'
    
    class RootElementParser:
        
        def __init__(self):
            self.id = None
            
        def start(self, tag, attrib):
            if tag == _('rpc'):
                self.id = int(attrib['message-id'])
            elif tag == _('notification'):
                self.id = 0
    
    target = RootElementParser()
    parser = ElementTree.XMLTreeBuilder(target=target)
    parser.feed(raw)
    return target.id
