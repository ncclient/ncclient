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

_capability_map = {
    'urn:liberouter:params:netconf:capability:power-control:1.0':
        [':power-control', ':power-control:1.0']
}

def _abbreviate(uri):
    if uri.startswith('urn:ietf:params:netconf:'):
        splitted = uri.split(':')
        if ':capability:' in uri:
            return [ ':' + splitted[5], ':' + splitted[5] + ':' + splitted[6] ]
        elif ':base:' in uri:
            return [ ':base', ':base' + ':'+ splitted[5] ]
    elif uri in _capability_map:
        return _capability_map[uri]
    return []

def schemes(url_uri):
    """Given a URI that has a *scheme* query string (i.e. *:url* capability
    URI), will return a list of supported schemes.
    """
    return url_uri.partition("?scheme=")[2].split(',')

class Capabilities:

    """Represents the set of capabilities for a NETCONF client or server.
    Initialised with a list of capability URI's.

    Presence of a capability can be checked with the *in* operations. In addition
    to the URI, for capabilities of the form
    *urn:ietf:params:netconf:capability:$name:$version* their shorthand can be
    used as a key. For example, for
    *urn:ietf:params:netconf:capability:candidate:1.0* the shorthand would be
    *:candidate*. If version is significant, use *:candidate:1.0* as key.
    """

    def __init__(self, capabilities):
        self._dict = {}
        for uri in capabilities:
            self._dict[uri] = _abbreviate(uri)

    def __contains__(self, key):
        if key in self._dict:
            return True
        for abbrs in self._dict.values():
            if key in abbrs:
                return True
        return False

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return self._dict.keys().__iter__()

    def __repr__(self):
        return repr(self._dict.keys())

    def __list__(self):
        return self._dict.keys()

    def add(self, uri):
        "Add a capability"
        self._dict[uri] = _abbreviate(uri)

    def remove(self, uri):
        "Remove a capability"
        if key in self._dict:
            del self._dict[key]

    def check(self, key):
        """Whether specified capability is present.

        :arg key: URI or shorthand

        .. note:
            The *in* operation is the preferred form.
        """
        return key in self

    def get_uri(self, shorthand):
        for uri, abbrs in self._dict.items():
            if shorthand in abbrs:
                return uri

#: :class:`Capabilities` object representing the capabilities currently supported by NCClient
CAPABILITIES = Capabilities([
    'urn:ietf:params:netconf:base:1.0',
    'urn:ietf:params:netconf:capability:writable-running:1.0',
    'urn:ietf:params:netconf:capability:candidate:1.0',
    'urn:ietf:params:netconf:capability:confirmed-commit:1.0',
    'urn:ietf:params:netconf:capability:rollback-on-error:1.0',
    'urn:ietf:params:netconf:capability:startup:1.0',
    'urn:ietf:params:netconf:capability:url:1.0?scheme=http,ftp,file,https,sftp',
    'urn:ietf:params:netconf:capability:validate:1.0',
    'urn:ietf:params:netconf:capability:xpath:1.0',
    'urn:liberouter:params:netconf:capability:power-control:1.0'
    #'urn:ietf:params:netconf:capability:notification:1.0', # TODO
    #'urn:ietf:params:netconf:capability:interleave:1.0' # theoretically already supported
])
