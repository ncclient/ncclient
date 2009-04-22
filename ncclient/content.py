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
from cStringIO import StringIO

logger = logging.getLogger('ncclient.content')


def qualify(tag, ns=None):
    if ns is None:
        return tag
    else:
        return '{%s}%s' % (ns, tag)
_ = qualify

################################################################################

class Hello:
    
    NS = 'urn:ietf:params:xml:ns:netconf:base:1.0'
    
    @staticmethod
    def build(capabilities, encoding='utf-8'):
        hello = ElementTree.Element(_('hello', Hello.NS))
        caps = ElementTree.Element('capabilities')
        for uri in capabilities:
            cap = ElementTree.Element('capability')
            cap.text = uri
            caps.append(cap)
        hello.append(caps)
        tree = ElementTree.ElementTree(hello)
        fp = StringIO()
        tree.write(fp, encoding)
        return fp.getvalue()
    
    @staticmethod
    def parse(raw):
        'Returns tuple of (session-id, ["capability_uri", ...])'
        id, capabilities = 0, []
        root = ElementTree.fromstring(raw)
        if root.tag == _('hello', Hello.NS):
            for child in root.getchildren():
                if child.tag == _('session-id', Hello.NS):
                    id = int(child.text)
                elif child.tag == _('capabilities', Hello.NS):
                    for cap in child.getiterator(_('capability', Hello.NS)):
                        capabilities.append(cap.text)
        return id, capabilities

################################################################################

class RootElementParser:
    
    '''Parse the root element of an XML document. The tag and namespace of
    recognized elements, and attributes of interest can be customized.
    
    RootElementParser does not parse any sub-elements.
    '''
    
    def __init__(self, recognize=[]):
        self._recognize = recognize
    
    def recognize(self, element):
        '''Specify an element that should be successfully parsed.
        
        element should be a string that represents a qualified name of the form
        *{namespace}tag*.
        '''
        self._recognize.append((element, attrs))
    
    def parse(self, raw):
        '''Parse the root element from a string representing an XML document.
        
        Returns a (tag, attributes) tuple. tag is a string representing
        the qualified name of the recognized element. attributes is a
        {'attr': value} dictionary.
        '''
        fp = StringIO(raw)
        for event, element in ElementTree.iterparse(fp, events=('start',)):
            for e in self._recognize:
                if element.tag == e:
                    return (element.tag, element.attrib)
            break
        return None


################################################################################

class XMLBuilder:
    
    @staticmethod
    def _element(spec):
        element = ElementTree.Element(spec['tag'], spec.get('attrib', {}))
        for child in spec.get('children', []):
            element.append(XMLBuilder._element(child))
        return element
    
    @staticmethod
    def _etree(spec):
        return ElementTree.ElementTree(XMLBuilder._element(spec))
    
    @staticmethod
    def build(spec, encoding='utf-8'):
        fp = StringIO()
        XMLBuilder._etree(spec).write(fp, encoding)
        return fp.get_value()
