:mod:`~ncclient.xml_` -- XML handling
=====================================

.. automodule:: ncclient.xml_
    :synopsis: XML handling

.. autoexception:: XMLError
    :show-inheritance:

Namespaces
-----------

.. autodata:: BASE_NS_1_0

.. autodata:: TAILF_AAA_1_1

.. autodata:: TAILF_EXECD_1_1

.. autodata:: CISCO_CPI_1_0

.. autodata:: JUNIPER_1_1

.. autodata:: FLOWMON_1_0

.. autofunction:: register_namespace(prefix, uri)

.. autofunction:: qualify

Conversion
-----------

.. autofunction:: to_xml

.. autofunction:: to_ele

.. autofunction:: parse_root

.. autofunction:: validated_element

