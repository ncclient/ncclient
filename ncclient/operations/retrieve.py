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

from ncclient.operations.errors import OperationError
from ncclient.operations.rpc import RPC, RPCReply

from ncclient.xml_ import *
from lxml import etree

from ncclient.operations import util

_VALID_WITH_DEFAULTS = [
    "explicit",
    "report-all",
    "report-all-tagged",
    "trim"
]

class WithDefaultsError(OperationError):

    """Raised when an invalid "with-defaults" option is specified in a Get or
       GetConfig request"""

    def __init__(self, invalid_mode):
        super(WithDefaultsError, self).__init__(
            "Invalid 'with-defaults' mode '{provided}', must be one of the "
            "following: {options}".format(
                provided=invalid_mode,
                options=', '.join(_VALID_WITH_DEFAULTS)
            ))

class GetReply(RPCReply):

    """Adds attributes for the *data* element to `RPCReply`."""

    def _parsing_hook(self, root):
        self._data = None
        if not self._errors:
            self._data = root.find(qualify("data"))

    @property
    def data_ele(self):
        "*data* element as an :class:`~xml.etree.ElementTree.Element`"
        if not self._parsed:
            self.parse()
        return self._data

    @property
    def data_xml(self):
        "*data* element as an XML string"
        if not self._parsed:
            self.parse()
        return to_xml(self._data)

    data = data_ele
    "Same as :attr:`data_ele`"


class GetSchemaReply(GetReply):
    """Reply for GetSchema called with specific parsing hook."""

    def _parsing_hook(self, root):
        self._data = None
        if not self._errors:
            self._data = root.find(qualify("data", NETCONF_MONITORING_NS)).text


class Get(RPC):

    "The *get* RPC."

    REPLY_CLS = GetReply
    "See :class:`GetReply`."

    def request(self, filter=None, with_defaults=None):
        """Retrieve running configuration and device state information.

        *filter* specifies the portion of the configuration to retrieve (by default entire configuration is retrieved)

        *with_defaults* defines an explicit method of retrieving default values from the configuration (see RFC 6243)

        :seealso: :ref:`filter_params`
        """
        node = new_ele("get")
        if filter is not None:
            node.append(util.build_filter(filter))
        if with_defaults is not None:
            self._assert(":with-defaults")
            _append_with_defaults(node, with_defaults)
        return self._request(node)

def _append_with_defaults(node, with_defaults):
    if with_defaults.strip().lower() not in _VALID_WITH_DEFAULTS:
        raise WithDefaultsError(with_defaults)
    with_defaults_ele = sub_ele_ns(node, "with-defaults", NETCONF_WITH_DEFAULTS_NS)
    with_defaults_ele.text = with_defaults

class GetConfig(RPC):

    """The *get-config* RPC."""

    REPLY_CLS = GetReply
    """See :class:`GetReply`."""

    def request(self, source, filter=None, with_defaults=None):
        """Retrieve all or part of a specified configuration.

        *source* name of the configuration datastore being queried

        *filter* specifies the portion of the configuration to retrieve (by default entire configuration is retrieved)

        *with_defaults* defines an explicit method of retrieving default values from the configuration (see RFC 6243)

        :seealso: :ref:`filter_params`"""
        node = new_ele("get-config")
        node.append(util.datastore_or_url("source", source, self._assert))
        if filter is not None:
            node.append(util.build_filter(filter))
        if with_defaults is not None:
            self._assert(":with-defaults")
            _append_with_defaults(node, with_defaults)
        return self._request(node)

class GetSchema(RPC):

    """The *get-schema* RPC."""

    REPLY_CLS = GetSchemaReply
    """See :class:`GetReply`."""

    def request(self, identifier, version=None, format=None):
        """Retrieve a named schema, with optional revision and type.

        *identifier* name of the schema to be retrieved

        *version* version of schema to get

        *format* format of the schema to be retrieved, yang is the default

        :seealso: :ref:`filter_params`"""
        node = etree.Element(qualify("get-schema",NETCONF_MONITORING_NS))
        if identifier is not None:
            elem = etree.Element(qualify("identifier",NETCONF_MONITORING_NS))
            elem.text = identifier
            node.append(elem)
        if version is not None:
            elem = etree.Element(qualify("version",NETCONF_MONITORING_NS))
            elem.text = version
            node.append(elem)
        if format is not None:
            elem = etree.Element(qualify("format",NETCONF_MONITORING_NS))
            elem.text = format
            node.append(elem)
        return self._request(node)

class Dispatch(RPC):

    """Generic retrieving wrapper"""

    REPLY_CLS = GetReply
    """See :class:`GetReply`."""

    def request(self, rpc_command, source=None, filter=None):
        """
        *rpc_command* specifies rpc command to be dispatched either in plain text or in xml element format (depending on command)

        *source* name of the configuration datastore being queried

        *filter* specifies the portion of the configuration to retrieve (by default entire configuration is retrieved)

        :seealso: :ref:`filter_params`

        Examples of usage::

            dispatch('clear-arp-table')

        or dispatch element like ::

            xsd_fetch = new_ele('get-xnm-information')
            sub_ele(xsd_fetch, 'type').text="xml-schema"
            sub_ele(xsd_fetch, 'namespace').text="junos-configuration"
            dispatch(xsd_fetch)
        """


        if etree.iselement(rpc_command):
            node = rpc_command
        else:
            node = new_ele(rpc_command)
        if source is not None:
            node.append(util.datastore_or_url("source", source, self._assert))
        if filter is not None:
            node.append(util.build_filter(filter))

        return self._request(node)
