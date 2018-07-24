"""
Handler for default device information.

Some devices require very specific information and action during client interaction.

The "device handlers" provide a number of callbacks that return the necessary
information. This allows the ncclient code to merely call upon this device handler -
once configured - instead of cluttering its code with if-statements.

Initially, not much is dealt with by the handler. However, in the future, as more
devices with specific handling are added, more handlers and more functions should be
implememted here, so that the ncclient code can use these callbacks to fill in the
device specific information.

Note that for proper import, the classname has to be:

    "<Devicename>DeviceHandler"

...where <Devicename> is something like "Default", "Nexus", etc.

All device-specific handlers derive from the DefaultDeviceHandler, which implements the
generic information needed for interaction with a Netconf server.

"""
import sys
if sys.version >= '3':
    xrange = range

class DefaultDeviceHandler(object):
    """
    Default handler for device specific information.

    """
    # Define the exempt error messages (those that shouldn't cause an exception).
    # Wild cards are possible: Start and/or end with a '*' to indicate that the text
    # can appear at the start, the end or the middle of the error message to still
    # match. All comparisons are case insensitive.
    _EXEMPT_ERRORS = []

    def __init__(self, device_params=None):
        self.device_params = device_params
        # Turn all exempt errors into lower case, since we don't want those comparisons
        # to be case sensitive later on. Sort them into exact match, wildcard start,
        # wildcard end, and full wildcard categories, depending on whether they start
        # and/or end with a '*'.
        self._exempt_errors_exact_match = []
        self._exempt_errors_startwith_wildcard_match = []
        self._exempt_errors_endwith_wildcard_match = []
        self._exempt_errors_full_wildcard_match = []
        for i in xrange(len(self._EXEMPT_ERRORS)):
            e = self._EXEMPT_ERRORS[i].lower()
            if e.startswith("*"):
                if e.endswith("*"):
                    self._exempt_errors_full_wildcard_match.append(e[1:-1])
                else:
                    self._exempt_errors_startwith_wildcard_match.append(e[1:])
            elif e.endswith("*"):
                self._exempt_errors_endwith_wildcard_match.append(e[:-1])
            else:
                self._exempt_errors_exact_match.append(e)


    def add_additional_ssh_connect_params(self, kwargs):
        """
        Add device specific parameters for the SSH connect.

        Pass in the keyword-argument dictionary for the SSH connect call. The
        dictionary will be modified (!) with the additional device-specific parameters.

        """
        pass


    def get_capabilities(self):
        """
        Return the capability list.

        A list of URI's representing the client's capabilities. This is used during
        the initial capability exchange. Modify (in a new device-handler subclass)
        as needed.

        """
        return [
            "urn:ietf:params:netconf:base:1.0",
            "urn:ietf:params:netconf:base:1.1",
            "urn:ietf:params:netconf:capability:writable-running:1.0",
            "urn:ietf:params:netconf:capability:candidate:1.0",
            "urn:ietf:params:netconf:capability:confirmed-commit:1.0",
            "urn:ietf:params:netconf:capability:rollback-on-error:1.0",
            "urn:ietf:params:netconf:capability:startup:1.0",
            "urn:ietf:params:netconf:capability:url:1.0?scheme=http,ftp,file,https,sftp",
            "urn:ietf:params:netconf:capability:validate:1.0",
            "urn:ietf:params:netconf:capability:xpath:1.0",
            "urn:ietf:params:netconf:capability:notification:1.0",
            "urn:liberouter:params:netconf:capability:power-control:1.0",
            "urn:ietf:params:netconf:capability:interleave:1.0",
            "urn:ietf:params:netconf:capability:with-defaults:1.0"
        ]

    def get_xml_base_namespace_dict(self):
        """
        A dictionary containing the base namespace.

        For lxml's nsmap, the base namespace should have a 'None' key.

            {
                None: "... base namespace... "
            }

        If no base namespace is needed, an empty dictionary should be
        returned.

        """
        return {}

    def get_xml_extra_prefix_kwargs(self):
        """
        Return any extra prefix that should be sent with each RPC request.

        Since these are used as kwargs, the function should return
        either an empty dictionary if there are no additional arguments,
        or a dictionary with keyword parameters suitable fo the Element()
        function. Mostly, this is the "nsmap" argument.

            {
                "nsmap" : {
                    ... namespace definitions ...
                }
            }

        """
        return {}

    def get_ssh_subsystem_names(self):
        """
        Return a list of names to try for the SSH subsystems.

        This always returns a list, even if only a single subsystem name is used.

        If the returned list contains multiple names then the various subsystems are
        tried in order, until one of them can successfully connect.

        """
        return [ "netconf" ]

    def is_rpc_error_exempt(self, error_text):
        """
        Check whether an RPC error message is excempt, thus NOT causing an exception.

        On some devices the RPC operations may indicate an error response, even though
        the operation actually succeeded. This may be in cases where a warning would be
        more appropriate. In that case, the client may be better advised to simply
        ignore that error and not raise an exception.

        Note that there is also the "raise_mode", set on session and manager, which
        controls the exception-raising behaviour in case of returned errors. This error
        filter here is independent of that: No matter what the raise_mode says, if the
        error message matches one of the exempt errors returned here, an exception
        will not be raised.

        The exempt error messages are defined in the _EXEMPT_ERRORS field of the device
        handler object and can be overwritten by child classes.  Wild cards are
        possible: Start and/or end with a '*' to indicate that the text can appear at
        the start, the end or the middle of the error message to still match. All
        comparisons are case insensitive.

        Return True/False depending on found match.

        """
        if error_text is not None:
            error_text = error_text.lower().strip()
        else:
            error_text = 'no error given'

        # Compare the error text against all the exempt errors.
        for ex in self._exempt_errors_exact_match:
            if error_text == ex:
                return True

        for ex in self._exempt_errors_startwith_wildcard_match:
            if error_text.endswith(ex):
                return True

        for ex in self._exempt_errors_endwith_wildcard_match:
            if error_text.startswith(ex):
                return True

        for ex in self._exempt_errors_full_wildcard_match:
            if ex in error_text:
                return True

        return False


    def perform_qualify_check(self):
        """
        During RPC operations, we perform some initial sanity checks on the responses.

        This check will fail for some devices, in which case this function here should
        return False in order to skip the test.

        """
        return True


    def add_additional_operations(self):
        """
        Add device/vendor specific operations.

        """
        return {}


    def handle_raw_dispatch(self, raw):
        return False


    def handle_connection_exceptions(self, sshsession):
        return False


    def transform_reply(self):
        return False
