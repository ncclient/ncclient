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

class Capabilities:
    
    def __init__(self, capabilities=None):
        self._dict = {}
        if isinstance(capabilities, dict):
            self._dict = capabilities
        elif isinstance(capabilities, list):
            for uri in capabilities:
                self._dict[uri] = Capabilities.guess_shorthand(uri)
    
    def __contains__(self, key):
        return ( key in self._dict ) or ( key in self._dict.values() )
    
    def __repr__(self):
        elems = ['<capability>%s</capability>' % uri for uri in self._dict]
        return ('<capabilities>%s</capabilities>' % ''.join(elems))
    
    def add(self, uri, shorthand=None):
        if shorthand is None:
            shorthand = Capabilities.guess_shorthand(uri)
        self._dict[uri] = shorthand
    
    set = add
    
    def remove(self, key):
        if key in self._dict:
            del self._dict[key]
        else:
            for uri in self._dict:
                if self._dict[uri] == key:
                    del self._dict[uri]
                    break
        
    @staticmethod
    def guess_shorthand(uri):
        if uri.startswith('urn:ietf:params:netconf:capability:'):
            return (':' + uri.split(':')[5])

    
CAPABILITIES = Capabilities([
    'urn:ietf:params:netconf:base:1.0',
    'urn:ietf:params:netconf:capability:writable-running:1.0',
    'urn:ietf:params:netconf:capability:candidate:1.0',
    'urn:ietf:params:netconf:capability:confirmed-commit:1.0',
    'urn:ietf:params:netconf:capability:rollback-on-error:1.0',
    'urn:ietf:params:netconf:capability:startup:1.0',
    'urn:ietf:params:netconf:capability:url:1.0',
    'urn:ietf:params:netconf:capability:validate:1.0',
    'urn:ietf:params:netconf:capability:xpath:1.0',
    'urn:ietf:params:netconf:capability:notification:1.0',
    'urn:ietf:params:netconf:capability:interleave:1.0'
    ])

if __name__ == "__main__":
    assert(':validate' in CAPABILITIES) # test __contains__
    print CAPABILITIES # test __repr__