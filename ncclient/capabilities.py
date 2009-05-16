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

def abbreviate(uri):
    if uri.startswith('urn:ietf:params:netconf:capability:'):
        return ':' + uri.split(':')[5]
    elif uri.startswith('urn:ietf:params:netconf:base:'):
        return ':base'

def version(uri):
    if uri.startswith('urn:ietf:params:netconf:capability:'):
        return uri.split(':')[6]
    elif uri.startswith('urn:ietf:params:netconf:base:'):
        return uri.split(':')[5]

class Capabilities:

    def __init__(self, capabilities=None):
        self._dict = {}
        if isinstance(capabilities, dict):
            self._dict = capabilities
        elif isinstance(capabilities, list):
            for uri in capabilities:
                self._dict[uri] = (abbreviate(uri), version(uri))

    def __contains__(self, key):
        if key in self._dict:
            return True
        for info in self._dict.values():
            if key == info[0]:
                return True
        return False

    def __iter__(self):
        return self._dict.keys().__iter__()

    def __repr__(self):
        return repr(self._dict.keys())

    def __list__(self):
        return self._dict.keys()

    def add(self, uri, info=None):
        if info is None:
            info = (abbreviate(uri), version(uri))
        self._dict[uri] = info

    set = add

    def remove(self, key):
        if key in self._dict:
            del self._dict[key]
        else:
            for uri in self._dict:
                if key in self._dict[uri]:
                    del self._dict[uri]
                    break

    def get_uri(self, shortname):
        for uri, info in self._dict.items():
            if info[0] == shortname:
                return uri

    def url_schemes(self):
        url_uri = get_uri(':url')
        if url_uri is None:
            return []
        else:
            return url_uri.partition("?scheme=")[2].split(',')

    def version(self, key):
        try:
            return self._dict[key][1]
        except KeyError:
            for uri, info in self._dict.items():
                if info[0] == key:
                    return info[1]


#: the capabilities supported by NCClient
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
    #'urn:ietf:params:netconf:capability:notification:1.0', # TODO
    #'urn:ietf:params:netconf:capability:interleave:1.0' # theoretically already supported
])
