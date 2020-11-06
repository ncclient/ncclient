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

from ncclient._types import Datastore
from ncclient._types import Origin
from ncclient.namespaces import IETF
from ncclient.operations.errors import OperationError
from ncclient.operations.rpc import RPC, RPCReply

from ncclient.xml_ import *
from lxml import etree

from ncclient.operations import util


class GetDataError(OperationError):
    """Generic error class returned from invalid GetData requests"""

class WithDefaultsError(OperationError):

    """Invalid 'with-defaults' mode or capability URI"""


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

        *with_defaults* defines an explicit method of retrieving default values from the configuration (see :rfc:`6243`)

        :seealso: :ref:`filter_params`
        """
        node = new_ele("get")
        if filter is not None:
            node.append(util.build_filter(filter))
        if with_defaults is not None:
            self._assert(":with-defaults")
            _append_with_defaults_mode(
                node,
                with_defaults,
                self._session.server_capabilities,
            )
        return self._request(node)


def _append_with_defaults_mode(node, mode, capabilities):
    _validate_with_defaults_mode(mode, capabilities)
    with_defaults_element = sub_ele_ns(
        node,
        "with-defaults",
        NETCONF_WITH_DEFAULTS_NS,
    )
    with_defaults_element.text = mode


def _validate_with_defaults_mode(mode, capabilities):
    valid_modes = _get_valid_with_defaults_modes(capabilities)
    if mode.strip().lower() not in valid_modes:
        raise WithDefaultsError(
            "Invalid 'with-defaults' mode '{provided}'; the server only "
            "supports the following: {options}".format(
                provided=mode,
                options=', '.join(valid_modes)
            )
        )


def _get_valid_with_defaults_modes(capabilities):
    """Reference: https://tools.ietf.org/html/rfc6243#section-4.3"""
    capability = capabilities[":with-defaults"]

    try:
        valid_modes = [capability.parameters["basic-mode"]]
    except KeyError:
        raise WithDefaultsError(
            "Invalid 'with-defaults' capability URI advertised by the server; "
            "missing 'basic-mode' parameter"
        )

    try:
        also_supported = capability.parameters["also-supported"]
    except KeyError:
        return valid_modes

    valid_modes.extend(also_supported.split(","))

    return valid_modes


class GetConfig(RPC):

    """The *get-config* RPC."""

    REPLY_CLS = GetReply
    """See :class:`GetReply`."""

    def request(self, source, filter=None, with_defaults=None):
        """Retrieve all or part of a specified configuration.

        *source* name of the configuration datastore being queried

        *filter* specifies the portion of the configuration to retrieve (by default entire configuration is retrieved)

        *with_defaults* defines an explicit method of retrieving default values from the configuration (see :rfc:`6243`)

        :seealso: :ref:`filter_params`"""
        node = new_ele("get-config")
        node.append(util.datastore_or_url("source", source, self._assert))
        if filter is not None:
            node.append(util.build_filter(filter))
        if with_defaults is not None:
            self._assert(":with-defaults")
            _append_with_defaults_mode(
                node,
                with_defaults,
                self._session.server_capabilities,
            )
        return self._request(node)


class GetData(RPC):
    """RFC8526 implementation of <get-data> RPC"""

    REPLY_CLS = GetReply
    """See :class:`GetReply`."""

    def request(self, datastore, filter=None, config_filter=False,
            origin_filters=[], negated_origin_filters=[], max_depth=None,
            with_origin=None, with_defaults=None, strip_ns=False):
        """Construct the request for the get-data RPC

        See RFC8526 for detailed explanations of all posssible input
        parameters as is a 1:1 relationship in most cases.

        Outside of the specification, if the caller specifies
        strip_ns=True, then the 'datastore' element will not contain a
        prefix xmlns declaration in addition the text content will not
        contain a prepended prefix.  This is necessary for some
        implementations that do not handle the namespace/prefix
        declaration properly.

        Args:
            datastore: A valid _types.Datastore enum value representing
                a datastore to query [mandatory]
            filter: A tuple, list or string representing filter data
            config_filter: A boolean value representing to only return
                config=true (r/w) nodes from the requested datastore
            origin_filters: A list of _types.Origin values
            negated_origin_filters: A list of _types.Origin values
            max_depth: None for 'unbounded', otherwise an integer value
                between 1-65535
            with_origin: A boolean value representing to return origin
                metadata in responses
            with_defaults: A _types.WithDefaults enum value
                representing to return default data according to
                RFC6243
            strip_ns: A boolean value to indicate skipping namespace
                qualification of the datastore node
        Returns:
            An ncclient.xml_.NCElement representing the serialized
            NETCONF RPC request.
        """

        if not isinstance(datastore, Datastore):
            datastores = [str(x) for x in Datastore]
            raise GetDataError(
                    "Invalid 'datastore' definition; must be one of "
                    "[{datastores}]".format(
                        datastores=', '.join(datastores)))

        node = new_ele('get-data', attrs={'xmlns': IETF.nsmap['ncds']})

        # Some implementations do not correctly support the namespace
        # and prefixing associated with ietf-datastores.  If the caller
        # sets strip_ns=True then skip the addition of the namespace
        # and prefix for the <datastore> element + value.
        if strip_ns:
            ds = sub_ele(node, 'datastore')
            ds.text = datastore.name.lower()
        else:
            ds = sub_ele(node, 'datastore',
                    nsmap={'ds': IETF.nsmap['ds']})
            ds.text = 'ds:' + datastore.name.lower()

        if config_filter:
            sub_ele(node, 'config-filter').text = 'true'

        if max_depth is not None:
            if type(max_depth) is int:
                if 1 <= max_depth <= 65535:
                    sub_ele(node, 'max-depth').text = str(max_depth)
                else:
                    raise GetDataError(
                            "Invalid 'max-depth' '{provided}'; value must "
                            "be between 1-65535".format(provided=max_depth))

            else:
                raise GetDataError(
                        "Invalid 'max-depth' '{provided}'; value must "
                        "be between 1-65535".format(provided=max_depth))

        if filter is not None:
            node.append(util.build_filter(filter, nmda=True))

        if with_origin:
            sub_ele(node, 'with-origin')

        if isinstance(origin_filters, list):
            if len(origin_filters) > 0:
                for origin in origin_filters:
                    if isinstance(origin, Origin):
                        of = sub_ele(node, 'origin-filter',
                                nsmap={'or': IETF.nsmap['or']})
                        of.text = 'or:' + origin.name.lower()
                    else:
                        origins = [str(x) for x in Origin]
                        raise GetDataError(
                                "Invalid 'origin-filter' definition; "
                                "must be one of [{origins}]".format(
                                    origins=', '.join(origins)))

        else:
            raise GetDataError("'origin-filter' must be a list")

        if isinstance(negated_origin_filters, list):
            if len(negated_origin_filters) > 0:
                for origin in negated_origin_filters:
                    if isinstance(origin, Origin):
                        of = sub_ele(node, 'negated-origin-filter',
                                nsmap={'or': IETF.nsmap['or']})
                        of.text = 'or:' + origin.name.lower()
                    else:
                        origins = [str(x) for x in Origin]
                        raise GetDataError(
                                "Invalid 'negated-origin-filter' "
                                "definition; must be one of "
                                "[{origins}]".format(
                                    origins=', '.join(origins)))

        else:
            raise GetDataError("'negated-origin-filter' must be a list")


        if with_defaults is not None:
            self._assert(":with-defaults")
            _append_with_defaults_mode(
                node,
                with_defaults.name.lower().replace('_', '-'),
                self._session.server_capabilities,
            )

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

    REPLY_CLS = RPCReply
    """See :class:`RPCReply`."""

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
