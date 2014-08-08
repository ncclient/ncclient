# Copyright 2009 Shikhar Bhushan
# Copyright 2011 Leonidas Poulopoulos
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

"Methods for creating, parsing, and dealing with XML and ElementTree objects."


import io

from StringIO import StringIO
from lxml import etree

# In case issues come up with XML generation/parsing
# make sure you have the ElementTree v1.2.7+ lib as
# well as lxml v3.0+

from ncclient import NCClientError

parser = etree.XMLParser(recover=True)

class XMLError(NCClientError):
    pass

### Namespace-related

#: Base NETCONF namespace
BASE_NS_1_0 = "urn:ietf:params:xml:ns:netconf:base:1.0"
# NXOS_1_0
NXOS_1_0 = "http://www.cisco.com/nxos:1.0"
# NXOS_IF
NXOS_IF = "http://www.cisco.com/nxos:1.0:if_manager"
#: Namespace for Tail-f core data model
TAILF_AAA_1_1 = "http://tail-f.com/ns/aaa/1.1"
#: Namespace for Tail-f execd data model
TAILF_EXECD_1_1 = "http://tail-f.com/ns/execd/1.1"
#: Namespace for Cisco data model
CISCO_CPI_1_0 = "http://www.cisco.com/cpi_10/schema"
#: Namespace for Flowmon data model
FLOWMON_1_0 = "http://www.liberouter.org/ns/netopeer/flowmon/1.0"
#: Namespace for Juniper 9.6R4. Tested with Junos 9.6R4+
JUNIPER_1_1 = "http://xml.juniper.net/xnm/1.1/xnm"
#: Namespace for Huawei data model
HUAWEI_1_1 = "http://www.huawei.com/netconf/vrp"
#: Namespace for H3C data model
H3C_1_0 = "http://www.h3c.com/netconf/config:1.0"
#
try:
    register_namespace = etree.register_namespace
except AttributeError:
    def register_namespace(prefix, uri):
        from xml.etree import ElementTree
        # cElementTree uses ElementTree's _namespace_map, so that's ok
        ElementTree._namespace_map[uri] = prefix

for (ns, pre) in {
    BASE_NS_1_0: 'nc',
    NXOS_1_0: 'nxos',
    NXOS_IF: 'if',
    TAILF_AAA_1_1: 'aaa',
    TAILF_EXECD_1_1: 'execd',
    CISCO_CPI_1_0: 'cpi',
    FLOWMON_1_0: 'fm',
    JUNIPER_1_1: 'junos',
}.items():
    register_namespace(pre, ns)

qualify = lambda tag, ns=BASE_NS_1_0: tag if ns is None else "{%s}%s" % (ns, tag)
"""Qualify a *tag* name with a *namespace*, in :mod:`~xml.etree.ElementTree` fashion i.e. *{namespace}tagname*."""


def to_xml(ele, encoding="UTF-8", pretty_print=False):
    "Convert and return the XML for an *ele* (:class:`~xml.etree.ElementTree.Element`) with specified *encoding*."
    xml = etree.tostring(ele, encoding=encoding, pretty_print=pretty_print)
    return xml if xml.startswith('<?xml') else '<?xml version="1.0" encoding="%s"?>%s' % (encoding, xml)

def to_ele(x):
    "Convert and return the :class:`~xml.etree.ElementTree.Element` for the XML document *x*. If *x* is already an :class:`~xml.etree.ElementTree.Element` simply returns that."
    return x if etree.iselement(x) else etree.fromstring(x, parser=parser)

def parse_root(raw):
    "Efficiently parses the root element of a *raw* XML document, returning a tuple of its qualified name and attribute dictionary."
    fp = StringIO(raw)
    for event, element in etree.iterparse(fp, events=('start',)):
        return (element.tag, element.attrib)

def validated_element(x, tags=None, attrs=None):
    """Checks if the root element of an XML document or Element meets the supplied criteria.

    *tags* if specified is either a single allowable tag name or sequence of allowable alternatives

    *attrs* if specified is a sequence of required attributes, each of which may be a sequence of several allowable alternatives

    Raises :exc:`XMLError` if the requirements are not met.
    """
    ele = to_ele(x)
    if tags:
        if isinstance(tags, basestring):
            tags = [tags]
        if ele.tag not in tags:
            raise XMLError("Element [%s] does not meet requirement" % ele.tag)
    if attrs:
        for req in attrs:
            if isinstance(req, basestring): req = [req]
            for alt in req:
                if alt in ele.attrib:
                    break
            else:
                raise XMLError("Element [%s] does not have required attributes" % ele.tag)
    return ele

XPATH_NAMESPACES = {
    're':'http://exslt.org/regular-expressions'
}

class NCElement(object):
    def __init__(self, result, transform_reply):
        self.__result = result
        self.__transform_reply = transform_reply
        self.__doc = self.remove_namespaces(self.__result)


    def xpath(self, expression):
        """
            return result for a call to lxml xpath()
            output will be a list
        """
        self.__expression = expression
        self.__namespaces = XPATH_NAMESPACES
        return self.__doc.xpath(self.__expression, namespaces=self.__namespaces)

    def find(self, expression):
        """return result for a call to lxml ElementPath find()"""
        self.__expression = expression
        return self.__doc.find(self.__expression)

    def findtext(self, expression):
        """return result for a call to lxml ElementPath findtext()"""
        self.__expression = expression
        return self.__doc.findtext(self.__expression)


    def __str__(self):
        """syntactic sugar for str() - alias to tostring"""
        return self.tostring

    @property
    def tostring(self):
        """return a pretty-printed string output for rpc reply"""
        parser = etree.XMLParser(remove_blank_text=True)
        outputtree = etree.XML(etree.tostring(self.__doc), parser)
        return etree.tostring(outputtree, pretty_print=True)

    @property
    def data_xml(self):
        """return an unmodified output for rpc reply"""
        return to_xml(self.__doc)

    def remove_namespaces(self, rpc_reply):
        """remove xmlns attributes from rpc reply"""
        self.__xslt=self.__transform_reply
        self.__parser = etree.XMLParser(remove_blank_text=True)
        self.__xslt_doc = etree.parse(io.BytesIO(self.__xslt), self.__parser)
        self.__transform = etree.XSLT(self.__xslt_doc)
        self.__root = etree.fromstring(str(self.__transform(etree.parse(StringIO(rpc_reply)))))
        return self.__root


new_ele = lambda tag, attrs={}, **extra: etree.Element(qualify(tag), attrs, **extra)

sub_ele = lambda parent, tag, attrs={}, **extra: etree.SubElement(parent, qualify(tag), attrs, **extra)
