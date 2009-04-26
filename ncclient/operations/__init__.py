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

'NETCONF Remote Procedure Calls (RPC) and protocol operations'

import logging
logger = logging.getLogger('ncclient.operations')

#from retrieve import Get, GetConfig
#from edit import EditConfig, DeleteConfig
from session import CloseSession, KillSession
from lock import Lock, Unlock
#from notification import CreateSubscription

__all__ = [
    #'Get',
    #'GetConfig',
    #'EditConfig',
    #'DeleteConfig',
    'Lock',
    'Unlock',
    'CloseSession',
    'KillSession',
#    'CreateSubscription',
]
