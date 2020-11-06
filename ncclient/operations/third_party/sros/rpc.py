from ncclient.xml_ import *

from ncclient.namespaces import Nokia
from ncclient.operations.retrieve import GetData
from ncclient.operations.rpc import RPC

def global_operations(node):
    """Instantiate an SR OS global operation action element

    Args:
        node: A string representing the top-level action for a
            given global operation.
    Returns:
        A tuple of 'lxml.etree._Element' values.  The first value
        represents the top-level YANG action element and the second
        represents the caller supplied initial node.
    """
    parent, child = yang_action('global-operations',
            attrs={'xmlns': Nokia.nsmap['oper-global']})
    ele = sub_ele(child, node)
    return (parent, ele)

class SrosGetData(GetData):
    """Override RFC8526 get-data RPC for SR OS datastore ns handling
    """

    def request(self, datastore, filter=None, config_filter=False,
            origin_filters=[], negated_origin_filters=[], max_depth=None,
            with_origin=None, with_defaults=None):
        """Construct the request for an SR OS specific get-data RPC

        See operations.retrieve.GetData.request for the parent
        implementation.

        This method marshals all inputs from the caller prepending an
        additional argument for special handling of the namespace
        element.

        NOTE: This helper method will be deprecated at some point in the
        future.

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
        Returns:
            A modified call to the parent class request which returns a
            ncclient.xml_.NCElement representing the serialized NETCONF
            RPC request.
        """
        ## Ensure call to super() is python2 compatible
        return super(SrosGetData, self).request(datastore, filter, config_filter,
                origin_filters, negated_origin_filters, max_depth,
                with_origin, with_defaults, strip_ns=True)

class MdCliRawCommand(RPC):
    def request(self, command=None):
        """Construct the request for the <md-cli-raw-command> RPC

        Marshal an SR OS MD-CLI command over NETCONF.  The returned
        results will be the raw CLI output encapsulated within XML
        elements for deserialization.

        Args:
            command: A string value representing an MD-CLI command to
                be invoked
        Returns:
            An ncclient.xml_.NCElement object representing the
            serialized NETCONF RPC request.
        """
        node, raw_cmd_node = global_operations('md-cli-raw-command')
        sub_ele(raw_cmd_node, 'md-cli-input-line').text = command
        self._huge_tree = True
        return self._request(node)
