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

logger = logging.getLogger('ncclient.content')

BASE_NS = 'urn:ietf:params:xml:ns:netconf:base:1.0'
NOTIFICATION_NS = 'urn:ietf:params:xml:ns:netconf:notification:1.0'

def qualify(tag, ns=BASE_NS):
    return '{%s}%s' % (ns, tag)

_ = qualify

def make_hello(capabilities):
    return '<hello xmlns="%s">%s</hello>' % (BASE_NS, capabilities)

def make_rpc(id, op):
    return '<rpc message-id="%s" xmlns="%s">%s</rpc>' % (id, BASE_NS, op)

def parse_hello(raw):
    from capabilities import Capabilities
    id, capabilities = 0, Capabilities()
    root = ElementTree.fromstring(raw)
    if root.tag == _('hello'):
        for child in root.getchildren():
            if child.tag == _('session-id'):
                id = int(child.text)
            elif child.tag == _('capabilities'):
                for cap in child.getiterator(_('capability')):
                    capabilities.add(cap.text)
    return id, capabilities

def parse_message_root(raw):
    from cStringIO import StringIO
    fp = StringIO(raw)
    for event, element in ElementTree.iterparse(fp, events=('start',)):
        if element.tag == _('rpc'):
            return element.attrib['message-id']
        elif element.tag == _('notification', NOTIFICATION_NS):
            return 'notification'
        else:
            return None