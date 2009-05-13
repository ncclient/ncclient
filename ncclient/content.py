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

from cStringIO import StringIO
from xml.etree import cElementTree as ET

from ncclient import NCClientError

class ContentError(NCClientError):
    pass

### Namespace-related

BASE_NS = 'urn:ietf:params:xml:ns:netconf:base:1.0'
NOTIFICATION_NS = 'urn:ietf:params:xml:ns:netconf:notification:1.0'
# and this is BASE_NS according to cisco devices...
CISCO_BS = 'urn:ietf:params:netconf:base:1.0'

try:
    register_namespace = ET.register_namespace
except AttributeError:
    def register_namespace(prefix, uri):
        from xml.etree import ElementTree
        # cElementTree uses ElementTree's _namespace_map, so that's ok
        ElementTree._namespace_map[uri] = prefix

# we'd like BASE_NS to be prefixed as "netconf"
register_namespace('netconf', BASE_NS)

qualify = lambda tag, ns=BASE_NS: tag if ns is None else '{%s}%s' % (ns, tag)

# deprecated
multiqualify = lambda tag, nslist=(BASE_NS, CISCO_BS): [qualify(tag, ns) for ns in nslist]

unqualify = lambda tag: tag[tag.rfind('}')+1:]

### XML with Python data structures

class DictTree:

    @staticmethod
    def Element(spec):
        if iselement(spec):
            return spec
        elif isinstance(spec, basestring):
            return XML.Element(spec)
        if not isinstance(spec, dict):
            raise ContentError("Invalid tree spec")
        if 'tag' in spec:
            ele = ET.Element(spec.get('tag'), spec.get('attributes', {}))
            ele.text = spec.get('text', '')
            ele.tail = spec.get('tail', '')
            subtree = spec.get('subtree', [])
            # might not be properly specified as list but may be dict
            if isinstance(subtree, dict):
                subtree = [subtree]
            for subele in subtree:
                ele.append(DictTree.Element(subele))
            return ele
        elif 'comment' in spec:
            return ET.Comment(spec.get('comment'))
        else:
            raise ContentError('Invalid tree spec')
    
    @staticmethod
    def XML(spec, encoding='UTF-8'):
        return Element.XML(DictTree.Element(spec), encoding)

class Element:
    
    @staticmethod
    def DictTree(ele):
        return {
            'tag': ele.tag,
            'attributes': ele.attrib,
            'text': ele.text,
            'tail': ele.tail,
            'subtree': [ Element.DictTree(child) for child in root.getchildren() ]
        }
    
    @staticmethod
    def XML(ele, encoding='UTF-8'):
        xml = ET.tostring(ele, encoding)
        if xml.startswith('<?xml'):
            return xml
        else:
            return '<?xml version="1.0" encoding="%s"?>%s' % (encoding, xml)

class XML:
    
    @staticmethod
    def DictTree(xml):
        return Element.DictTree(XML.Element(xml))
    
    @staticmethod
    def Element(xml):
        return ET.fromstring(xml)

dtree2ele = DictTree.Element
dtree2xml = DictTree.XML
ele2dtree = Element.DictTree
ele2xml = Element.XML
xml2dtree = XML.DictTree
xml2ele = XML.Element

### Other utility functions

iselement = ET.iselement

def find(ele, tag, strict=True, nslist=[BASE_NS, CISCO_BS]):
    """In strict mode, doesn't work around Cisco implementations sending incorrectly namespaced XML. Supply qualified tag name if using strict mode.
    """
    if strict:
        return ele.find(tag)
    else:
        for qname in multiqualify(tag):
            found = ele.find(qname)
            if found is not None:
                return found        

def parse_root(raw):
    """
    """
    fp = StringIO(raw[:1024]) # this is a guess but start element beyond 1024 bytes would be a bit absurd
    for event, element in ET.iterparse(fp, events=('start',)):
        return (element.tag, element.attrib)

def validated_element(rep, tag, attrs=None):
    """
    """
    ele = dtree2ele(rep)
    if ele.tag not in (tag, qualify(tag)):
        raise ContentError("Required root element [%s] not found" % tag)
    if attrs is not None:
        for req in attrs:
            for attr in ele.attrib:
                if unqualify(attr) == req:
                    break
            else:
                raise ContentError("Required attribute [%s] not found in element [%s]" % (req, req_tag))
    return ele
