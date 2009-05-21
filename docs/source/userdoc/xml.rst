**********************
:mod:`content` module
**********************

.. automodule:: ncclient.xml_
    :synopsis: XML facilities

Namespaces
==========

The following namespace is defined in this module.

.. autodata:: BASE_NS

Namespaces are handled just the same way as :mod:`~xml.etree.ElementTree`. So a qualified name takes the form *{namespace}tag*. There are some utility functions for qualified names:

.. function:: qualify(tag[, ns=BASE_NS])
    
    :returns: qualified name

.. function:: unqualify(tag)
    
    :returns: unqualified name
    
    .. note:: It is strongly recommended to compare qualified names.

.. _dtree:

DictTree XML representation
===========================

.. note::
    Where this representation is stipulated, an XML literal or :class:`~xml.etree.ElementTree.Element` is just fine as well.

:mod:`ncclient` can make use of a special syntax for XML based on Python dictionaries. It is best illustrated through an example::
    
    dtree = {
        'tag': qualify('a', 'some_namespace'),
        'attrib': {'attr': 'val'},
        'subtree': [ { 'tag': 'child1' }, { 'tag': 'child2', 'text': 'some text' } ]
    }

Calling :func:`dtree2xml` on *dtree* would return

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ns0:a attr="val" xmlns:ns0="some_namespace">
        <child1 />
        <child2>some text</child2>
    </ns0:a>
    
In addition to a 'pure' dictionary representation a DictTree node (including the root) may be an XML literal or an :class:`~xml.etree.ElementTree.Element` instance. The above example could thus be equivalently written as::

    dtree2 = {
        'tag': '{ns}a',
        'attrib': {'attr': 'val'},
        'subtree': [ ET.Element('child1'), '<child2>some text</child2>' ]
    }

Converting between different representations
============================================

Conversions *to* DictTree representation are guaranteed to be entirely dictionaries. In converting *from* DictTree representation, the argument may be any valid representation as specified.

.. autofunction:: dtree2ele(spec)

.. autofunction:: dtree2xml(spec[, encoding="UTF-8"])

.. autofunction:: ele2dtree(ele)
    
.. autofunction:: ele2xml(ele)

.. autofunction:: xml2dtree(xml)

.. autofunction:: xml2ele(xml)

Other utility functions
========================

.. autofunction:: iselement(obj)

    :see: :meth:`xml.etree.ElementTree.iselement`

.. autofunction:: find(ele, tag[, nslist=[]])

.. autofunction:: parse_root(raw)

.. autofunction:: validated_element(rep, tag=None, attrs=None, text=None)


Errors
======

.. autoexception:: ContentError
    :show-inheritance:
    :members:

