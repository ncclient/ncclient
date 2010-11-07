:mod:`~ncclient.capabilities` -- NETCONF Capabilities
=====================================================

.. module:: ncclient.capabilities

.. autofunction:: schemes

.. autoclass:: Capabilities

    :members:

    .. describe:: ":cap" in caps

        Check for the presence of capability. In addition to the URI, for capabilities of the form `urn:ietf:params:netconf:capability:$name:$version` their shorthand can be used as a key. For example, for `urn:ietf:params:netconf:capability:candidate:1.0` the shorthand would be `:candidate`. If version is significant, use `:candidate:1.0` as key.

    .. describe:: iter(caps)

        Return an iterator over the full URI's of capabilities represented by this object.