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

from xml.etree import cElementTree as ElementTree

from . import NETCONF_NS
from .util import qualify as _

def make(id, op):
    return '<rpc message-id="%s" xmlns="%s">%s</rpc>' % (id, NETCONF_NS, op)

#def parse(raw):
#    
#    class RootElementParser:
#        
#        def __init__(self):
#            self.id = 0
#            self.is_notification = False
#            
#        def start(self, tag, attrib):
#            if tag == _('rpc'):
#                self.id = int(attrib['message-id'])
#            elif tag == _('notification'):
#                self.is_notification = True
#    
#    target = RootElementParser()
#    parser = ElementTree.XMLTreeBuilder(target=target)
#    parser.feed(raw)
#    return target.id, target.is_notification
#
