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

"TODO: docstring"

from xml.etree import cElementTree as ET

from ncclient import NCClientError

class ContentError(NCClientError):
    pass

### Namespace-related ###

BASE_NS = 'urn:ietf:params:xml:ns:netconf:base:1.0'
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

qualify = lambda tag, ns=BASE_NS: '{%s}%s' % (ns, tag)

# i would have written a def if lambdas weren't so much fun
multiqualify = lambda tag, nslist=(BASE_NS, CISCO_BS): [qualify(tag, ns)
                                                        for ns in nslist]

unqualify = lambda tag: tag[tag.rfind('}')+1:]

### XML with Python data structures

def to_element(spec):
    "TODO: docstring"
    if iselement(spec):
        return spec
    elif isinstance(spec, basestring):
        return ET.XML(spec)
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
            ele.append(XMLConverter.build(subele))
        return ele
    elif 'comment' in spec:
        return ET.Comment(spec.get('comment'))
    else:
        raise ContentError('Invalid tree spec')

def from_xml(xml):
    return ET.fromstring(xml)

def to_xml(repr, encoding='utf-8'):
    "TODO: docstring"
    xml = ET.tostring(to_element(repr), encoding)
    # some etree versions don't include xml decl with utf-8
    # this is a problem with some devices
    return (xml if xml.startswith('<?xml')
            else '<?xml version="1.0" encoding="%s"?>%s' % (encoding, xml))


## Utility functions

iselement = ET.iselement

def namespaced_find(ele, tag, strict=False):
    """In strict mode, doesn't work around Cisco implementations sending incorrectly
    namespaced XML. Supply qualified name if using strict mode.
    """
    found = None
    if strict:
        found = ele.find(tag)
    else:
        for qname in multiqualify(tag):
            found = ele.find(qname)
            if found is not None:
                break
    return found

def parse_root(raw):
    '''Internal use.
    Parse the top-level element from XML string.
    
    Returns a `(tag, attributes)` tuple, where `tag` is a string representing
    the qualified name of the root element and `attributes` is an
    `{attribute: value}` dictionary.
    '''
    fp = StringIO(raw[:1024]) # this is a guess but start element beyond 1024 bytes would be a bit absurd
    for event, element in ET.iterparse(fp, events=('start',)):
        return (element.tag, element.attrib)

def root_ensured(rep, req_tag, req_attrs=None):
    rep = to_element(rep)
    if rep.tag not in (req_tag, qualify(req_tag)):
        raise ContentError("Required root element [%s] not found" % req_tag)
    if req_attrs is not None:
        pass # TODO
    return rep
