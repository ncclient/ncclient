# -*- coding: utf-8 -*-
"""
IOS-XR custom RPC classes
=========================

Defines IOS-XR RPC specific classes.

"""

# import third party
from lxml import etree

# import ncclient
from ncclient.xml_ import *
from ncclient.operations import util
from ncclient.operations.rpc import RPC


class ExecuteRpc(RPC):

    """
    Executes arbitrary RPC requests.
    """

    def request(self, rpc_command):

        """
        Sends the RPC request as-is to the device.

        :param rpc_command: The XML RPC request either as string/text either as XML object.
        """
        if etree.iselement(rpc_command):
            node = rpc_command
        else:
            node = etree.fromstring(rpc_command)
        return self._request(node)


class GetConfiguration(RPC):

    """
    Retrieves config of specific configuration source.
    """

    def request(self, source=None, filter=None):

        """
        Builds the NETCONF <get-config> Request using the specified options.

        :param source: Use specifiec configuration source: running/startup/candidate. Default: running.
        :param filter: Filters the XML reply tree.
        """
        if source is None:
            source = 'running'
        get_config = new_ele('get-config')
        if filter is not None:
            filter_tree = sub_ele(get_config, 'filter')
            if etree.iselement(filter):
                filter_elem = filter
            else:
                filter_elem = etree.fromstring(filter)
            filter_tree.append(filter_elem)
        get_config.append(util.datastore_or_url('source', source, self._assert))
        return self._request(get_config)


class Get(RPC):

    """
    Retrieves running config.
    """

    def request(self, filter=None):

        """
        Builds the NETCONF <get-config> Request for the running config, using the specified filter.

        :param filter: Filters the XML reply tree.
        """

        get_config = new_ele('get-config')
        if filter is not None:
            filter_tree = sub_ele(get_config, 'filter')
            if etree.iselement(filter):
                filter_elem = filter
            else:
                filter_elem = etree.fromstring(filter)
            filter_tree.append(filter_elem)
        get_config.append(util.datastore_or_url('source', 'running', self._assert))
        return self._request(get_config)
