# Copyright 2h009 Shikhar Bhushan
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

'Locking-related NETCONF operations'

from ncclient.xml_ import *

from rpc import RPC

# TODO:
# should have some way to parse session-id from a lock-denied error, and raise
# a tailored exception

class Lock(RPC):

    "*<lock>* RPC"
    
    def request(self, target):
        """
        :arg target: see :ref:`source_target`
        :type target: string

        :rtype: :ref:`return`
        """
        node = new_ele("lock")
        sub_ele(sub_ele(node, "target"), "running")
        return self._request(node)


class Unlock(RPC):

    "*<unlock>* RPC"
    
    def request(self, target):
        """
        :arg target: see :ref:`source_target`
        :type target: string

        :rtype: :ref:`return`
        """
        node = new_ele("unlock")
        sub_ele(sub_ele(node, "target"), "running")
        return self._request(node)


class LockContext:

    """
    A context manager for the :class:`Lock` / :class:`Unlock` pair of RPC's.
    
    RPC errors are always raised as exceptions.
    
    Initialise with session instance (:class:`Session
    <ncclient.transport.Session>`) and lock target (:ref:`source_target`)
    """

    def __init__(self, session, target):
        self.session = session
        self.target = target

    def __enter__(self):
        Lock(self.session).request(self.target)
        return self

    def __exit__(self, *args):
        Unlock(self.session).request(self.target)
        return False
