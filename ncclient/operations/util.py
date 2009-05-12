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

from ncclient import content

from errors import OperationError, MissingCapabilityError

def one_of(*args):
    'Verifies that only one of the arguments is not None'
    for i, arg in enumerate(args):
        if arg is not None:
            for argh in args[i+1:]:
                if argh is not None:
                    raise OperationError('Too many parameters')
            else:
                return
    raise OperationError('Insufficient parameters')

def store_or_url(wha, loc, capcheck=None):
    node = { 'tag': wha, 'subtree': {} }
    if '://' in loc: # e.g. http://, file://, ftp://
        if capcheck is not None:
            capcheck(':url') # url schema check at some point!
        node['subtree']['tag'] = 'url'
        node['subtree']['text'] = loc
    else:
        node['subtree']['tag'] = loc
    return node

def build_filter(spec, capcheck=None):
    type = None
    if isinstance(spec, tuple):
        type, criteria = tuple
        rep = {
            'tag': 'filter',
            'attributes': {'type': type},
            'subtree': criteria
        }
    else:
        rep = content.validated_element(spec, 'filter', 'type')
        try:
            type = rep['type']
        except KeyError:
            type = ele[content.qualify('type')]
    if type == 'xpath' and capcheck is not None:
        capcheck(':xpath')
    return rep
