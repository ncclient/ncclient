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

'Boilerplate ugliness'

import enum

from ncclient._types import FilterType
from ncclient.xml_ import *
from ncclient.operations.errors import OperationError, MissingCapabilityError
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

def one_of(*args):
    "Verifies that only one of the arguments is not None"
    for i, arg in enumerate(args):
        if arg is not None:
            for argh in args[i+1:]:
                if argh is not None:
                    raise OperationError("Too many parameters")
            else:
                return
    raise OperationError("Insufficient parameters")

def datastore_or_url(wha, loc, capcheck=None):
    node = new_ele(wha)
    if "://" in loc: # e.g. http://, file://, ftp://
        if capcheck is not None:
            capcheck(":url") # url schema check at some point!
            sub_ele(node, "url").text = loc
    else:
        #if loc == 'candidate':
        #    capcheck(':candidate')
        #elif loc == 'startup':
        #    capcheck(':startup')
        #elif loc == 'running' and wha == 'target':
        #    capcheck(':writable-running')
        sub_ele(node, loc)
    return node

def build_filter(filter_spec, nmda=False):
    """Construct an XPath, Subtree or notification event filter

    A filter_spec can be passed in in the form of a tuple, list or
    string.

    If the filter_spec is a tuple, the first value must be a filter_type
    of either a string (e.g. 'xpath' or 'subtree') [preserved for
    backwards compatibility] or a _types.FilterType enum value.  The
    second value represents filter_data that can be represented either
    as a string (XML data or  an XPath expression) or a tuple where the
    first value indicates a  namespace map (dict of prefix:namespaces).

    If the filter_spec is a list, then the assumption is that it is a
    list of string XML elements to be constructed into a subtree
    filter.  This method of filter passing is legacy and preserved for
    backwards compatibility.

    If the filter_spec is a string, then the assumption is that the
    filter is solely for a NETCONF notification event stream filter.

    If 'nmda' is set to True from the caller, an NMDA compliant payload
    that conforms to newer filter styles will be produced.

    Args:
        filter_spec: A tuple, list or string representing filter data
        nmda: A boolean value indicating usage of NMDA compliant
            filters
    Returns:
        An lxml.etree._Element representing the filter type and filter
        data to be utilized among various RPCs.
    """
    filter_type = None

    if isinstance(filter_spec, tuple):
        filter_type, filter_data = filter_spec

        if (filter_type == FilterType.SUBTREE or
                filter_type == 'subtree'):
            if nmda:
                data = new_ele('subtree-filter')
            else:
                if isinstance(filter_type, enum.Enum):
                    filter_type = filter_type.name.lower()
                data = new_ele('filter', type=filter_type)
            data.append(to_ele(filter_data))

        elif (filter_type == FilterType.XPATH or
                filter_type == 'xpath'):
            # Parse the filter data if passed in as a tuple indicating
            # a namespace map is included.  The namespace map is the
            # first tuple item followed by the XPath expression
            if isinstance(filter_data, tuple):
                ns, select = filter_data
                if nmda:
                    data = new_ele_nsmap('xpath-filter', ns)
                    data.text = select
                else:
                    if isinstance(filter_type, enum.Enum):
                        filter_type = filter_type.name.lower()
                    data = new_ele_nsmap('filter', ns, type=filter_type)
                    data.attrib['select'] = select

            else:
                if nmda:
                    data = new_ele('xpath-filter')
                    data.text = filter_data
                else:
                    if isinstance(filter_type, enum.Enum):
                        filter_type = filter_type.name.lower()
                    data = new_ele('filter', type=filter_type)
                    data.attrib['select'] = filter_data

        else:
            raise OperationError('Invalid filter type')

    # If the filter_spec passed in is a list, then the assumption is
    # that it is a list of elements to be constructed as a subtree
    # filter since a filter type is not specified.  This method of
    # passing a filter is legacy and preserved for backwards
    # compatibility.
    elif isinstance(filter_spec, list):
        if nmda:
            data = new_ele('subtree-filter')
        else:
            data = new_ele('filter', type='subtree')

        for ele in filter_spec:
            data.append(to_ele(ele))

    else:
        data = validated_element(filter_spec, ('filter', qualify('filter'),
            qualify('filter', ns=NETCONF_NOTIFICATION_NS)))

    return data

def validate_args(arg_name, value, args_list):
    # this is a common method, which used to check whether a value is in args_list
    if value not in args_list:
        raise OperationError('Invalid value "%s" in "%s" element' % (value, arg_name))
    return True

def url_validator(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
