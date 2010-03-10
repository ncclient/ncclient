:mod:`~ncclient.xml_` -- XML handling
=====================================

.. module:: ncclient.xml_
    :synopsis: XML handling

.. autoexception:: XMLError
    :show-inheritance:

Namespaces
-----------

.. autodata:: BASE_NS_1_0

.. autodata:: TAILF_AAA_1_1

.. autodata:: TAILF_EXECD_1_1

.. autodata:: CISCO_CPI_1_0

.. autodata:: FLOWMON_1_0

.. function:: register_namespace(prefix, uri)
    
    ElementTree's namespace map determines the prefixes for namespace URI's when serializing to XML.
    This method allows modifying this map to specify a prefix for a namespace URI.

.. autofunction:: qualify

Conversion
-----------

.. autofunction:: to_xml

.. autofunction:: to_ele

.. autofunction:: parse_root

.. autofunction:: validated_element

.. 