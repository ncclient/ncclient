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
from Queue import Queue
from threading import Lock
from xml.etree import cElementTree as ET


def parse_root(raw):
    '''Parse the top-level element from a string representing an XML document.
    
    Returns a `(tag, attributes)` tuple, where `tag` is a string representing
    the qualified name of the root element and `attributes` is an
    `{attribute: value}` dictionary.
    '''
    fp = StringIO(raw)
    for event, element in ET.iterparse(fp, events=('start',)):
        return (element.tag, element.attrib)


class Subject(object):

    def __init__(self):
        "TODO: docstring"
        self._q = Queue()
        self._listeners = set([])
        self._lock = Lock()
    
    def _dispatch_received(self, raw):
        "TODO: docstring"
        root = parse_root(raw)
        with self._lock:
            listeners = list(self._listeners)
        for l in listeners:
            l.callback(root, raw)
    
    def _dispatch_error(self, err):
        "TODO: docstring"
        with self._lock:
            listeners = list(self._listeners)
        for l in listeners:
            l.errback(err)
    
    def add_listener(self, listener):
        "TODO: docstring"
        with self._lock:
            self._listeners.add(listener)
    
    def remove_listener(self, listener):
        "TODO: docstring"
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
    
    def send(self, message):
        "TODO: docstring"
        logger.debug('queueing:%s' % message)
        self._q.put(message)


class Listener(object):
    
    "TODO: docstring"
    
    def callback(self, root, raw):
        raise NotImplementedError
    
    def errback(self, err):
        raise NotImplementedError
