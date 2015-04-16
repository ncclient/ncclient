# Copyright 2015 Christian Jurk <christian.jurk@kaiaglobal.com>
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

##
# Compatibility functions.
##

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,
    text_type = str
    binary_type = bytes

    import io
    BytesIO = io.BytesIO
    StringIO = io.StringIO
    range_ = range
    from queue import Queue
else:
    string_types = basestring,
    text_type = unicode
    binary_type = str

    from StringIO import StringIO
    BytesIO = StringIO
    range_ = xrange
    from Queue import Queue


def force_bytes(data):
    """
    Returns a 8-bit string.

    :param data: Data
    :return: binary_type
    """
    if PY3 and isinstance(data, string_types):
        return data.encode('ascii')
    return data


def force_text(data):
    """
    Returns a unicode string.

    :param data: Data
    :return: text_type
    """
    if PY3 and isinstance(data, binary_type):
        return data.decode('ascii')
    elif PY2 and isinstance(data, binary_type):
        return data.decode('ascii')
    return data


def iteritems(d, **kwargs):
    """
    Wrapper for iterating over a dictionary's items.

    :param d: dict
    :param kwargs: Optional keyword arguments
    :return: iterator
    """
    if PY3:
        return iter(d.items(**kwargs))
    else:
        return d.iteritems(**kwargs)


def iterkeys(d, **kwargs):
    """
    Wrapper for iterating over a dictionary's keys.

    :param d: dict
    :param kwargs: Optional keyword arguments
    :return: iterator
    """
    if PY3:
        return iter(d.keys(**kwargs))
    else:
        return d.iterkeys(**kwargs)

def with_metaclass(meta, *bases):
    """
    Create a base class with meta class.

    :param meta: Meta class
    :param bases: Base class(es)
    :return: Replaced version of the class
    """
    class metaclass(meta):
        def __new__(cls, name, thos_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})