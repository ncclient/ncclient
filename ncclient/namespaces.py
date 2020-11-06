# Copyright 2020 Ebben Aries
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

class IETF(object):
    # YANG module prefix -> namespace map
    nsmap = {
        'ds':      'urn:ietf:params:xml:ns:yang:ietf-datastores',
        'nc':      'urn:ietf:params:xml:ns:netconf:base:1.0',
        'ncds':    'urn:ietf:params:xml:ns:yang:ietf-netconf-nmda',
        'ncm':     'urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring',
        'ncwd':    'urn:ietf:params:xml:ns:yang:ietf-netconf-with-defaults',
        'or':      'urn:ietf:params:xml:ns:yang:ietf-origin'
    }

    # Namespaces that are not defined in a YANG module and thus do not
    # have a prefix declaration for mapping
    notif = 'urn:ietf:params:xml:ns:netconf:notification:1.0'
    yang = 'urn:ietf:params:xml:ns:yang:1'


class Nokia(object):
    nsmap = {
        'conf':        'urn:nokia.com:sros:ns:yang:sr:conf',
        'oper-global': 'urn:nokia.com:sros:ns:yang:sr:oper-global',
        'state':       'urn:nokia.com:sros:ns:yang:sr:state'
    }
