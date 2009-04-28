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
        return (element.tag, element.attrib)
