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
    "Raised by methods of the :mod:`content` module in case of an error."
    pass

### Namespace-related

# : Base NETCONf namespace
BASE_NS = 'urn:ietf:params:xml:ns:netconf:base:1.0'
# : ... and this is BASE_NS according to Cisco devices tested
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
        """DictTree -> Element

        :type spec: :obj:`dict` or :obj:`string` or :class:`~xml.etree.ElementTree.Element`

        :rtype: :class:`~xml.etree.ElementTree.Element`
        """
        if iselement(spec):
            return spec
        elif isinstance(spec, basestring):
            return XML.Element(spec)
        if not isinstance(spec, dict):
            raise ContentError("Invalid tree spec")
        if 'tag' in spec:
            ele = ET.Element(spec.get('tag'), spec.get('attrib', {}))
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
        """DictTree -> XML

        :type spec: :obj:`dict` or :obj:`string` or :class:`~xml.etree.ElementTree.Element`

        :arg encoding: chraracter encoding

        :rtype: string
        """
        return Element.XML(DictTree.Element(spec), encoding)

class Element:

    @staticmethod
    def DictTree(ele):
        """DictTree -> Element

        :type spec: :class:`~xml.etree.ElementTree.Element`
        :rtype: :obj:`dict`
        """
        return {
            'tag': ele.tag,
            'attributes': ele.attrib,
            'text': ele.text,
            'tail': ele.tail,
            'subtree': [ Element.DictTree(child) for child in root.getchildren() ]
        }

    @staticmethod
    def XML(ele, encoding='UTF-8'):
        """Element -> XML

        :type spec: :class:`~xml.etree.ElementTree.Element`
        :arg encoding: character encoding
        :rtype: :obj:`string`
        """
        xml = ET.tostring(ele, encoding)
        if xml.startswith('<?xml'):
            return xml
        else:
            return '<?xml version="1.0" encoding="%s"?>%s' % (encoding, xml)

class XML:

    @staticmethod
    def DictTree(xml):
        """XML -> DictTree

        :type spec: :obj:`string`
        :rtype: :obj:`dict`
        """
        return Element.DictTree(XML.Element(xml))

    @staticmethod
    def Element(xml):
        """XML -> Element

        :type xml: :obj:`string`
        :rtype: :class:`~xml.etree.ElementTree.Element`
        """
        return ET.fromstring(xml)

dtree2ele = DictTree.Element
dtree2xml = DictTree.XML
ele2dtree = Element.DictTree
ele2xml = Element.XML
xml2dtree = XML.DictTree
xml2ele = XML.Element

### Other utility functions

iselement = ET.iselement

def find(ele, tag, nslist=[]):
    """If `nslist` is empty, same as :meth:`xml.etree.ElementTree.Element.find`. If it is not, `tag` is interpreted as an unqualified name and qualified using each item in `nslist`. The first match is returned.

    :arg nslist: optional list of namespaces
    """
    if nslist:
        for qname in multiqualify(tag):
            found = ele.find(qname)
            if found is not None:
                return found
    else:
        return ele.find(tag)

def parse_root(raw):
    """Efficiently parses the root element of an XML document.

    :type raw: string
    :returns: a tuple of `(tag, attributes)`, where `tag` is the (qualified) name of the element and `attributes` is a dictionary of its attributes.
    """
    fp = StringIO(raw[:1024]) # this is a guess but start element beyond 1024 bytes would be a bit absurd
    for event, element in ET.iterparse(fp, events=('start',)):
        return (element.tag, element.attrib)

def validated_element(rep, tag=None, attrs=None, text=None):
    """Checks if the root element meets the supplied criteria. Returns a :class:`~xml.etree.ElementTree.Element` instance if so, otherwise raises :exc:`ContentError`.

    :arg tag: tag name or a list of allowable tag names
    :arg attrs: list of required attribute names, each item may be a list of allowable alternatives
    :arg text: textual content to match
    :type rep: :obj:`dict` or :obj:`string` or :class:`~xml.etree.ElementTree.Element`
    """
    ele = dtree2ele(rep)
    err = False
    if tag:
        if isinstance(tag, basestring): tag = [tag]
        if ele.tag not in tags:
            err = True
    if attrs:
        for req in attrs:
            if isinstance(req, basestring): req = [req]
            for alt in req:
                if alt in ele.attrib:
                    break
            else:
                err = True
    if text and ele.text != text:
        err = True
    if err:
        raise ContentError("Element [%s] does not meet requirements" % ele.tag)
    return ele
