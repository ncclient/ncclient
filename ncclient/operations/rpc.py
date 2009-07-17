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

from threading import Event, Lock
from uuid import uuid1

from ncclient import xml_
from ncclient.transport import SessionListener

from errors import OperationError, TimeoutExpiredError, MissingCapabilityError

import logging
logger = logging.getLogger('ncclient.operations.rpc')


class RPCReply:

    """Represents an *<rpc-reply>*. Only concerns itself with whether the
    operation was successful.

    .. note::
        If the reply has not yet been parsed there is an implicit, one-time
        parsing overhead to accessing the attributes defined by this class and
        any subclasses.
    """

    def __init__(self, raw):
        self._raw = raw
        self._parsed = False
        self._root = None
        self._errors = []

    def __repr__(self):
        return self._raw

    def _parsing_hook(self, root):
        """Subclass can implement.

        :type root: :class:`~xml.etree.ElementTree.Element`
        """
        pass

    def parse(self):
        """Parse the *<rpc-reply>*"""
        if self._parsed:
            return
        root = self._root = xml_.xml2ele(self._raw) # <rpc-reply> element
        # per rfc 4741 an <ok/> tag is sent when there are no errors or warnings
        ok = xml_.find(root, 'ok', nslist=xml_.NSLIST)
        if ok is not None:
            logger.debug('parsed [%s]' % ok.tag)
        else: # create RPCError objects from <rpc-error> elements
            error = xml_.find(root, 'rpc-error', nslist=xml_.NSLIST)
            if error is not None:
                logger.debug('parsed [%s]' % error.tag)
                for err in root.getiterator(error.tag):
                    # process a particular <rpc-error>
                    d = {}
                    for err_detail in err.getchildren(): # <error-type> etc..
                        tag = xml_.unqualify(err_detail.tag)
                        if tag != 'error-info':
                            d[tag] = err_detail.text.strip()
                        else:
                            d[tag] = xml_.ele2xml(err_detail)
                    self._errors.append(RPCError(d))
        self._parsing_hook(root)
        self._parsed = True

    @property
    def xml(self):
        "*<rpc-reply>* as returned"
        return self._raw

    @property
    def ok(self):
        "Boolean value indicating if there were no errors."
        if not self._parsed:
            self.parse()
        return not self._errors # empty list => false

    @property
    def error(self):
        """Short for :attr:`errors` [0]; :const:`None` if there were no errors.
        """
        if not self._parsed:
            self.parse()
        if self._errors:
            return self._errors[0]
        else:
            return None

    @property
    def errors(self):
        """`list` of :class:`RPCError` objects. Will be empty if there were no
        *<rpc-error>* elements in reply.
        """
        if not self._parsed:
            self.parse()
        return self._errors


class RPCError(OperationError): # raise it if you like

    """Represents an *<rpc-error>*. It is an instance of :exc:`OperationError`
    and can be raised like any other exception."""

    def __init__(self, err_dict):
        self._dict = err_dict
        if self.message is not None:
            OperationError.__init__(self, self.message)
        else:
            OperationError.__init__(self)

    @property
    def type(self):
        "`string` representing text of *error-type* element"
        return self.get('error-type', None)

    @property
    def severity(self):
        "`string` representing text of *error-severity* element"
        return self.get('error-severity', None)

    @property
    def tag(self):
        "`string` representing text of *error-tag* element"
        return self.get('error-tag', None)

    @property
    def path(self):
        "`string` or :const:`None`; representing text of *error-path* element"
        return self.get('error-path', None)

    @property
    def message(self):
        "`string` or :const:`None`; representing text of *error-message* element"
        return self.get('error-message', None)

    @property
    def info(self):
        "`string` (XML) or :const:`None`, representing *error-info* element"
        return self.get('error-info', None)

    ## dictionary interface

    __getitem__ = lambda self, key: self._dict.__getitem__(key)

    __iter__ = lambda self: self._dict.__iter__()

    __contains__ = lambda self, key: self._dict.__contains__(key)

    keys = lambda self: self._dict.keys()

    get = lambda self, key, default: self._dict.get(key, default)

    iteritems = lambda self: self._dict.iteritems()

    iterkeys = lambda self: self._dict.iterkeys()

    itervalues = lambda self: self._dict.itervalues()

    values = lambda self: self._dict.values()

    items = lambda self: self._dict.items()

    __repr__ = lambda self: repr(self._dict)


class RPCReplyListener(SessionListener):

    # internal use

    # one instance per session -- maybe there is a better way??
    def __new__(cls, session):
        instance = session.get_listener_instance(cls)
        if instance is None:
            instance = object.__new__(cls)
            instance._lock = Lock()
            instance._id2rpc = {}
            #instance._pipelined = session.can_pipeline
            session.add_listener(instance)
        return instance

    def register(self, id, rpc):
        with self._lock:
            self._id2rpc[id] = rpc

    def callback(self, root, raw):
        tag, attrs = root
        if xml_.unqualify(tag) != 'rpc-reply':
            return
        for key in attrs: # in the <rpc-reply> attributes
            if xml_.unqualify(key) == 'message-id': # if we found msgid attr
                id = attrs[key] # get the msgid
                try:
                    with self._lock:
                        rpc = self._id2rpc.get(id) # the corresponding rpc
                        logger.debug('delivering to %r' % rpc)
                        rpc.deliver_reply(raw)
                except KeyError:
                    raise OperationError('Unknown message-id: %s', id)
                # no catching other exceptions, fail loudly if must
                else:
                    # if no error delivering, can del the reference to the RPC
                    del self._id2rpc[id]
                    break
        else:
            raise OperationError('Could not find "message-id" attribute in <rpc-reply>')
    
    def errback(self, err):
        try:
            for rpc in self._id2rpc.values():
                rpc.deliver_error(err)
        finally:
            self._id2rpc.clear()


class RPC(object):

    """Base class for all operations.

    Directly corresponds to *<rpc>* requests. Handles making the request, and
    taking delivery of the reply.
    """

    #: Subclasses can specify their dependencies on capabilities. List of URI's
    # or abbreviated names, e.g. ':writable-running'. These are verified at the
    # time of object creation. If the capability is not available, a
    # :exc:`MissingCapabilityError` is raised.
    DEPENDS = []

    #: Subclasses can specify a different reply class, but it must be a
    # subclass of :class:`RPCReply`.
    REPLY_CLS = RPCReply

    def __init__(self, session, async=False, timeout=None, raise_mode='none'):
        self._session = session
        try:
            for cap in self.DEPENDS:
                self._assert(cap)
        except AttributeError:
            pass
        self._async = async
        self._timeout = timeout
        self._raise_mode = raise_mode
        # keeps things simple instead of having a class attr that has to be locked
        self._id = uuid1().urn
        self._listener = RPCReplyListener(session)
        self._listener.register(self._id, self)
        self._reply = None
        self._error = None
        self._event = Event()

    def _build(self, opspec):
        # internal
        spec = {
            'tag': 'rpc',
            'attrib': {
                'xmlns': xml_.BASE_NS_1_0,
                'message-id': self._id
                },
            'subtree': [ opspec ]
            }
        return xml_.dtree2xml(spec)

    def _request(self, op):
        """Subclasses call this method to make the RPC request.
        
        In synchronous mode, waits until the reply is received and returns
        :class:`RPCReply`.
        
        In asynchronous mode, returns immediately, returning a reference to this
        object. The :attr:`event` attribute will be set when the reply has been
        received (see :attr:`reply`) or an error occured (see :attr:`error`).
        
        :arg opspec: :ref:`dtree` for the operation
        :type opspec: :obj:`dict` or :obj:`string` or :class:`~xml.etree.ElementTree.Element`
        :rtype: :class:`RPCReply` (sync) or :class:`RPC` (async)
        """
        logger.debug('request %r with opsepc=%r' % (self, op))
        req = self._build(op)
        self._session.send(req)
        if self._async:
            logger.debug('async, returning')
            return self
        else:
            logger.debug('sync, will wait for timeout=%r' % self._timeout)
            self._event.wait(self._timeout)
            if self._event.isSet():
                if self._error:
                    # Error that prevented reply delivery
                    raise self._error
                self._reply.parse()
                if self._reply.error is not None:
                    # <rpc-error>'s [ RPCError ]
                    if self._raise_mode == "all":
                        raise self._reply.error
                    elif (self._raise_mode == "errors" and
                          self._reply.error.type == "error"):
                        raise self._reply.error
                return self._reply
            else:
                raise TimeoutExpiredError

    def request(self, *args, **kwds):
        """Subclasses implement this method. Here, the operation is constructed
        in :ref:`dtree`, and the result of :meth:`_request` returned."""
        return self._request(self.SPEC)
    
    def _assert(self, capability):
        """Subclasses can use this method to verify that a capability is available
        with the NETCONF server, before making a request that requires it. A
        :exc:`MissingCapabilityError` will be raised if the capability is not
        available."""
        if capability not in self._session.server_capabilities:
            raise MissingCapabilityError('Server does not support [%s]' %
                                         capability)
    
    def deliver_reply(self, raw):
        # internal use
        self._reply = self.REPLY_CLS(raw)
        #self._delivery_hook() -- usecase?!
        self._event.set()

    def deliver_error(self, err):
        # internal use
        self._error = err
        #self._delivery_hook() -- usecase?!
        self._event.set()

    @property
    def reply(self):
        ":class:`RPCReply` element if reply has been received or :const:`None`"
        return self._reply

    @property
    def error(self):
        """:exc:`Exception` type if an error occured or :const:`None`.
        
        .. note::
            This represents an error which prevented a reply from being
            received. An *<rpc-error>* does not fall in that category -- see
            :class:`RPCReply` for that.
        """
        return self._error

    @property
    def id(self):
        "The *message-id* for this RPC"
        return self._id

    @property
    def session(self):
        """The :class:`~ncclient.transport.Session` object associated with this
        RPC"""
        return self._session

    @property
    def event(self):
        """:class:`~threading.Event` that is set when reply has been received or
        error occured."""
        return self._event

    def set_async(self, async=True):
        """Set asynchronous mode for this RPC."""
        self._async = async
        if async and not session.can_pipeline:
            raise UserWarning('Asynchronous mode not supported for this device/session')

    def set_raise_mode(self, mode):
        assert(choice in ('all', 'errors', 'none'))
        self._raise_mode = mode

    def set_timeout(self, timeout):
        """Set the timeout for synchronous waiting defining how long the RPC
        request will block on a reply before raising an error."""
        self._timeout = timeout

    #: Whether this RPC is asynchronous
    async = property(fget=lambda self: self._async, fset=set_async)

    #: Timeout for synchronous waiting
    timeout = property(fget=lambda self: self._timeout, fset=set_timeout)
