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

################################################################################
# Namespace-related

BASE_NS = 'urn:ietf:params:xml:ns:netconf:base:1.0'

# cisco returns incorrectly namespaced xml
CISCO_BS = 'urn:ietf:params:netconf:base:1.0'

# we'd like BASE_NS to be prefixed as "netconf"
try:
    register_namespace = ET.register_namespace
except AttributeError:
    def register_namespace(prefix, uri):
        from xml.etree import ElementTree
        # cElementTree uses ElementTree's _namespace_map, so that's ok
        ElementTree._namespace_map[uri] = prefix

register_namespace('netconf', BASE_NS)

qualify = lambda tag, ns: '{%s}%s' % (namespace, tag)

unqualify = lambda tag: tag[tag.rfind('}')+1:]


################################################################################
# Build XML using Python data structures :-)

class TreeBuilder:
    """Build an ElementTree.Element instance from an XML tree specification
    based on nested dictionaries. TODO: describe spec
    """
    
    def __init__(self, spec):
        "TODO: docstring"
        self._root = TreeBuilder.build(spec)
        
    def to_string(self, encoding='utf-8'):
        "TODO: docstring"
        xml = ET.tostring(self._root, encoding)
        # some etree versions don't always include xml decl
        # this is a problem with some devices
        if not xml.startswith('<?xml'):
            return '<?xml version="1.0" encoding="%s"?>%s' % (encoding, xml)
        else:
            return xml
    
    @property
    def tree(self):
        "TODO: docstring"
        return self._root
    
    @staticmethod
    def build(spec):
        "TODO: docstring"
        if spec.has_key('tag'):
            ele = ET.Element(spec.get('tag'), spec.get('attributes', {}))
            ele.text = spec.get('text', '')
            children = spec.get('children', [])
            if isinstance(children, dict):
                children = [children]
            for child in children:
                ele.append(TreeBuilder.build(child))
            return ele
        elif spec.has_key('comment'):
            return ET.Comment(spec.get('comment'))
        else:
            raise ValueError('Invalid tree spec')

################################################################################