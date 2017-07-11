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


from ncclient.operations.rpc import RPC
from ncclient.operations.rpc import RPCReply
from ncclient.xml_ import *
from ncclient.transport.session import SessionListener
from ncclient.operations import util
from ncclient.operations.errors import YangPushError
from dateutil.parser import parse


class CreateSubscription(RPC):
    
    "`create-subscription` RPC. Depends on the `:notification` capability."

    DEPENDS = [':notification']

    def request(self, filter=None, stream_name=None, start_time=None, stop_time=None):
        """Creates a subscription for notifications from the server.

        *filter* specifies the subset of notifications to receive (by
        default all notificaitons are received)

        :seealso: :ref:`filter_params`

        *stream_name* specifies the notification stream name. The
        default is None meaning all streams.

        *start_time* triggers the notification replay feature to
        replay notifications from the given time. The default is None,
        meaning that this is not a replay subscription. The format is
        an RFC 3339/ISO 8601 date and time.

        *stop_time* indicates the end of the notifications of
        interest. This parameter must be used with *start_time*. The
        default is None, meaning that (if *start_time* is present) the
        notifications will continue until the subscription is
        terminated. The format is an RFC 3339/ISO 8601 date and time.

        """
        node = new_ele_ns("create-subscription", NETCONF_NOTIFICATION_NS)
        if filter is not None:
            node.append(util.build_filter(filter))
        if stream_name is not None:
            sub_ele(node, "stream").text = stream_name

        if start_time is not None:
            sub_ele(node, "startTime").text = start_time

        if stop_time is not None:
            if start_time is None:
                raise ValueError("You must provide start_time if you provide stop_time")
            sub_ele(node, "stopTime").text = stop_time

        return self._request(node)


#
# Message with period specified
#
period_template = '''<?xml version="1.0" encoding="UTF-8"?>
<rpc message-id="{}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
 <establish-subscription xmlns="urn:ietf:params:xml:ns:yang:ietf-event-notifications"
   xmlns:yp="urn:ietf:params:xml:ns:yang:ietf-yang-push">
  <stream>yp:yang-push</stream>
  <yp:xpath-filter>{}</yp:xpath-filter>
  <yp:period>{}</yp:period>
 </establish-subscription>
</rpc>'''


#
# Message with dampening-period specified
#
dampening_period_template = '''<?xml version="1.0" encoding="UTF-8"?>
<rpc message-id="{}" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
 <establish-subscription xmlns="urn:ietf:params:xml:ns:yang:ietf-event-notifications"
   xmlns:yp="urn:ietf:params:xml:ns:yang:ietf-yang-push">
  <stream>yp:yang-push</stream>
  <yp:xpath-filter>{}</yp:xpath-filter>
  <yp:dampening-period>{}</yp:dampening-period>
 </establish-subscription>
</rpc>'''


class EstablishSubscriptionReply(RPCReply):

    """Establish Subscription Result RPCReply Class."""
    
    def _parsing_hook(self, root):
        self._result = None
        self._subscription_id = None
        if not self._errors:
            self._subscription_result = root.find(
                qualify("subscription-result", IETF_EVENT_NOTIFICATIONS_NS))
            self._subscription_id = root.find(
                qualify("subscription-id", IETF_EVENT_NOTIFICATIONS_NS))

    @property
    def subscription_result(self):
        "*subscription-result* element as an :class:`~xml.etree.ElementTree.Element`"
        if not self._parsed:
            self.parse()
        return self._subscription_result.text

    @property
    def subscription_result_ele(self):
        "*subscription-result* element as an :class:`~xml.etree.ElementTree.Element`"
        if not self._parsed:
            self.parse()
        return self._subscription_result

    @property
    def subscription_result_xml(self):
        "*subscription-result* element as an XML string"
        if not self._parsed:
            self.parse()
        return to_xml(self._subscription_result)

    @property
    def subscription_id(self):
        "*subscription-id* element as an :class:`~xml.etree.ElementTree.Element`"
        if not self._parsed:
            self.parse()
        return int(self._subscription_id.text)

    @property
    def subscription_id_ele(self):
        "*subscription-id* element as an :class:`~xml.etree.ElementTree.Element`"
        if not self._parsed:
            self.parse()
        return self._subscription_id

    @property
    def subscription_id_xml(self):
        "*subscription-id* element as an XML string"
        if not self._parsed:
            self.parse()
        return to_xml(self._subscription_id)


class EstablishSubscription(RPC):
    
    "`establish-subscription` RPC"

    # DEPENDS = [':ietf-yang-push']
    REPLY_CLS = EstablishSubscriptionReply
    
    def request(self, callback, errback, xpath=None, period=None, dampening_period=None):
        """Create a simple subscription for ietf-yang-push subscriptions.

        *callback* user-defined callback for notifications

        *errback* user-defined error handling callback

        *xpath* specifies the xpath-filter element

        *period* period for polling; on-change implied if not set

        *dampening_period* dampening period for change events

        RPC currently supports only stream `yang-push`.
        """
        #
        # validate parameters
        #
        if xpath is None:
            raise YangPushError("Must have xpath")
        if period and dampening_period:
            raise YangPushError("Can only have one of period and dampening_period")
        if (period is None) and (dampening_period is None):
            raise YangPushError("Must have at least one of period or dampening_period")

        #
        # start constructing request
        #
        # node = new_ele_ns("establish-subscription", IETF_EVENT_NOTIFICATIONS_NS)
        # stream = sub_ele_ns(node, "stream", IETF_EVENT_NOTIFICATIONS_NS)
        # stream.text = 'yp:yang-push'
        # stream.attrib = { 'xmlns:yp': IETF_YANG_PUSH_NS }
        # sub_ele_ns(node, "xpath-filter", IETF_YANG_PUSH_NS).text = xpath
        # if period:
        #     sub_ele_ns(node, "period", IETF_YANG_PUSH_NS).text = str(period)
        # elif dampening_period:
        #     sub_ele_ns(node, "dampening-period", IETF_YANG_PUSH_NS).text = str(dampening_period)

        # Have to hack request as can't figure out how to force NS
        # inclusion for identity values yet!
        if period:
            rpc = period_template.format(self._id, xpath, period)
        else:
            rpc = dampening_period_template.format(self._id, xpath, dampening_period)

        # install a listener
        self.session.add_listener(YangPushListener(callback, errback))

        # Now process the request
        return self._request(None, raw_xml=rpc)


class DeleteSubscriptionReply(RPCReply):

    """Delete Subscription Result RPCReply Class."""
    
    def _parsing_hook(self, root):
        self._result = None
        self._subscription_id = None
        if not self._errors:
            self._subscription_result = root.find(
                qualify("subscription-result", IETF_EVENT_NOTIFICATIONS_NS))

    @property
    def subscription_result(self):
        "*subscription-result* element as an :class:`~xml.etree.ElementTree.Element`"
        if not self._parsed:
            self.parse()
        return self._subscription_result.text

    @property
    def subscription_result_ele(self):
        "*subscription-result* element as an :class:`~xml.etree.ElementTree.Element`"
        if not self._parsed:
            self.parse()
        return self._subscription_result

    @property
    def subscription_result_xml(self):
        "*subscription-result* element as an XML string"
        if not self._parsed:
            self.parse()
        return to_xml(self._subscription_result)


class DeleteSubscription(RPC):
    
    "`establish-subscription` RPC"

    # DEPENDS = [':ietf-yang-push']
    REPLY_CLS = DeleteSubscriptionReply
    
    def request(self, subscription_id=None):
        """Create a simple subscription for ietf-yang-push subscriptions.

        *subscription_id* the id of the subscription to delete

        """
        #
        # validate parameters
        #
        if subscription_id is None:
            raise YangPushError("Must provide subscription_id")

        #
        # Construct request
        #
        node = new_ele_ns("delete-subscription", IETF_EVENT_NOTIFICATIONS_NS)
        to_delete = sub_ele_ns(node, "subscription-id", IETF_EVENT_NOTIFICATIONS_NS)
        to_delete.text = str(subscription_id)

        # Now process the request
        return self._request(node)


class YangPushNotificationType(object):

    """Simple enumeration of YANG push notification types."""
    
    UNKNOWN = 0
    PUSH_UPDATE = 1
    PUSH_CHANGE_UPDATE = 2

    @staticmethod
    def str_to_type(string):
        lookup = {
            "push-update": YangPushNotificationType.PUSH_UPDATE,
            "push-change-update": YangPushNotificationType.PUSH_CHANGE_UPDATE,
        }
        try:
            return lookup[string]
        except:
            raise Exception("Unknown YANG push notification type")


class YangPushNotification(object):

    """Represents a YANG Push `notification`."""
    
    def __init__(self, raw):
        self._raw = raw
        self._parsed = False
        self._root = None
        self._datastore = None
        self._event_time = None
        self._subscription_id = None
        self._type = None
        self._invalid = False
        
    def __repr__(self):
        return self._raw
    
    def parse(self):
        try:
            root = self._root = to_ele(self._raw)

            # extract eventTime
            event_time = root.find(qualify("eventTime", NETCONF_NOTIFICATION_NS))
            if event_time is not None:
                self._event_time = parse(event_time.text)

            # determine type of event
            type = root.find(qualify("push-update", IETF_YANG_PUSH_NS))
            if type is not None:
                self._type = YangPushNotificationType.PUSH_UPDATE
                self._datastore = root.find(
                    './/%s' % qualify('datastore-contents-xml', IETF_YANG_PUSH_NS))
            else:
                type = root.find(qualify("push-change-update", IETF_YANG_PUSH_NS))
                if type is not None:
                    self._type = YangPushNotificationType.PUSH_CHANGE_UPDATE
                    self._datastore = root.find(
                        './/%s' % qualify('datastore-changes-xml', IETF_YANG_PUSH_NS))
                else:
                    self.type = YangPushNotificationType.UNKNOWN

            # extract subscription-id
            if type is not None:
                subscription_id = type.find(qualify("subscription-id", IETF_YANG_PUSH_NS))
                if subscription_id is not None:
                    self._subscription_id = int(subscription_id.text)

            # flag that we're parsed now
            self._parsed = True

        except Exception as e:
            self._invalid = True
            
    @property
    def xml(self):
        return self._raw

    @property
    def event_time(self):
        if not self._parsed:
            self.parse()
        return self._event_time

    @property
    def subscription_id(self):
        if not self._parsed:
            self.parse()
        return self._subscription_id

    @property
    def type(self):
        if not self._parsed:
            self.parse()
        return self._type

    @property
    def datastore_ele(self):
        if not self._parsed:
            self.parse()
        return self._datastore

    @property
    def datastore_xml(self):
        if not self._parsed:
            self.parse()
        return etree.tostring(self._datastore)

    @property
    def root_ele(self):
        if not self._parsed:
            self.parse()
        return self._root

    @property
    def root_xml(self):
        if not self._parsed:
            self.parse()
        return etree.tostring(self._root)


class YangPushListener(SessionListener):

    """Class extending :class:`Session` listeners, which are notified when
    a new RFC 5277 notification is received or an error occurs.
    """

    def __init__(self, user_callback, user_errback):
        """Called by EstablishSubscription when a new NotificationListener is
        added to a session.  used to keep track of connection and
        subscription info in case connection gets dropped.
        """
        self.user_callback = user_callback
        self.user_errback = user_errback

    def callback(self, root, raw):
        """Called when a new RFC 5277 notification is received.

        The *root* argument allows the callback to determine whether
        the message is a notification.  Here, *root* is a tuple of
        *(tag, attributes)* where *tag* is the qualified name of the
        root element and *attributes* is a dictionary of its
        attributes (also qualified names).  *raw* will contain the xml
        notification as a string.
        """
        tag, attrs = root
        if tag != qualify("notification", NETCONF_NOTIFICATION_NS):
            # we just ignore any message not a notification
            return
        self.user_callback(YangPushNotification(raw))

    def errback(self, ex):
        """Called when an error occurs.
        For now just handles a dropped connection.
        :type ex: :exc:`Exception`
        """
        self.user_errback(ex)
