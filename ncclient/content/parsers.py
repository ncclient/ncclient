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

from xml.etree import cElementTree as ET

from common import BASE_NS
from common import qualify as _

class HelloParser:

    @staticmethod
    def parse(raw):
        'Returns tuple of (session-id, ["capability_uri", ...])'
        sid, capabilities = 0, []
        root = ET.fromstring(raw)
        if root.tag == _('hello', BASE_NS):
            for child in root.getchildren():
                if child.tag == _('session-id', BASE_NS):
                    sid = child.text
                elif child.tag == _('capabilities', BASE_NS):
                    for cap in child.getiterator(_('capability', BASE_NS)):
                        capabilities.append(cap.text)
        return sid, capabilities


class RootParser:
    '''Parser for the top-level element of an XML document. Does not look at any
    sub-elements. It is useful for determining the type of received messages.
    '''
    
    def __init__(self, recognize=[]):
        self._recognized = recognize
    
    def recognize(self, element):
        '''Specify an element that should be successfully parsed.
        
        element should be a string that represents a qualified name of the form
        `{namespace}tag`.
        '''
        self._recognized.append(element)
    
    def parse(self, raw):
        '''Parse the top-level element from a string representing an XML document.
        
        Returns a `(tag, attributes)` tuple, where `tag` is a string representing
        the qualified name of the recognized element and `attributes` is an
        `{attribute: value}` dictionary.
        '''
        fp = StringIO(raw)
        for event, element in ET.iterparse(fp, events=('start',)):
            for ele in self._recognize:
                if element.tag == ele:
                    return (element.tag, element.attrib)
            break
        return None