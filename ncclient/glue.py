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

"TODO: docstring"

from cStringIO import StringIO
from threading import Thread, Lock
from xml.etree import cElementTree as ET

import logging
logger = logging.getLogger('ncclient.glue')


def parse_root(raw):
    '''Parse the top-level element from a string representing an XML document.
    
    Returns a `(tag, attributes)` tuple, where `tag` is a string representing
    the qualified name of the root element and `attributes` is an
    `{attribute: value}` dictionary.
    '''
    fp = StringIO(raw[:1024]) # this is a guess but start element beyond 1024 bytes would be a bit absurd
    for event, element in ET.iterparse(fp, events=('start',)):
        return (element.tag, element.attrib)


class Subject(Thread):
    
    'Meant for subclassing by transport.Session'

    def __init__(self):
        "TODO: docstring"
        Thread.__init__(self)
        self._listeners = set() # TODO(?) weakref
        self._lock = Lock()
    
    def _dispatch_message(self, raw):
        "TODO: docstring"
        try:
            root = parse_root(raw)
        except Exception as e:
            logger.error('error parsing dispatch message: %s' % e)
            return
        with self._lock:
            listeners = list(self._listeners)
        for l in listeners:
            logger.debug('dispatching message to %r' % l)
            try:
                l.callback(root, raw)
            except Exception as e:
                logger.warning('[error] %r' % e)
    
    def _dispatch_error(self, err):
        "TODO: docstring"
        with self._lock:
            listeners = list(self._listeners)
        for l in listeners:
            logger.debug('dispatching error to %r' % l)
            try:
                l.errback(err)
            except Exception as e:
                logger.warning('error %r' % e)
    
    def add_listener(self, listener):
        "TODO: docstring"
        logger.debug('installing listener %r' % listener)
        with self._lock:
            self._listeners.add(listener)
    
    def remove_listener(self, listener):
        "TODO: docstring"
        logger.debug('discarding listener %r' % listener)
        with self._lock:
            self._listeners.discard(listener)
    
    def get_listener_instance(self, cls):
        '''This is useful when we want to maintain one listener of a particular
        type per subject i.e. a multiton.
        '''
        with self._lock:
            for listener in self._listeners:
                if isinstance(listener, cls):
                    return listener


class Listener(object):
    
    "TODO: docstring"
    
    def callback(self, root, raw):
        raise NotImplementedError
    
    def errback(self, err):
        raise NotImplementedError
