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
from cStringIO import StringIO

from common import BASE_NS
from common import qualify as _
from common import unqualify as __

class HelloParser:

    @staticmethod
    def parse(raw):
        'Returns tuple of (session-id, ["capability_uri", ...])'
        sid, capabilities = 0, []
        root = ET.fromstring(raw)
        # cisco's too posh to namespace its hello
        if __(root.tag) == 'hello':
            for child in root.getchildren():
                if __(child.tag) == 'session-id':
                    sid = child.text
                elif __(child.tag) == 'capabilities':
                    for cap in child.getiterator('capability'): 
                        capabilities.append(cap.text)
                    for cap in child.getiterator(_('capability', BASE_NS)):
                        capabilities.append(cap.text)
        return sid, capabilities


class RootParser:
    '''Parser for the top-level element of an XML document. Does not look at any
    sub-elements. It is useful for efficiently determining the type of a received
    message.
    '''
    
    @staticmethod
    def parse(raw, recognized=[]):
        '''Parse the top-level element from a string representing an XML document.
        
        recognized is a list of tag names that will be successfully parsed.
        The tag names should be qualified with namespace.
        
        Returns a `(tag, attributes)` tuple, where `tag` is a string representing
        the qualified name of the recognized element and `attributes` is an
        `{attribute: value}` dictionary.
        '''
        fp = StringIO(raw)
        for event, element in ET.iterparse(fp, events=('start',)):
            for ele in recognized:
                if element.tag == ele:
                    return (element.tag, element.attrib)
            break


class RPCReplyParser:
    
    @staticmethod
    def parse_rpc_error(root, ns):
        err_dict = {}
        for tag in ('error-type', 'error-tag', 'error-severity', 'error-app-tag',
                    'error-path', 'error-message', 'error-info'):
            ele = root.find(_(tag, ns))
            if ele is not None:
                err_dict[tag] = ele.text
        
    @staticmethod
    def parse(raw):
        oktags = (_('ok', BASE_NS), _('ok', CISCO_NS))
        root = ET.fromstring(raw)
        ok = root.find(_('ok', BASE_NS))
        if ok is None:
            ok = root.find(_('ok', CISCO_BS))
        ns = BASE_NS
        errs = root.findall(_('rpc-error', BASE_NS))
        if not errs:
            errs = root.findall(_('rpc-error', CISCO_BS))
            ns = CISCO_NS
        ret = [ (err, RPCReplyParser.parse_rpc_error(err, ns)) for err in errs ]
        return ok, ret
