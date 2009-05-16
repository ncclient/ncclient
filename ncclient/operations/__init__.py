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

from errors import OperationError, MissingCapabilityError
from rpc import RPC, RPCReply, RPCError
from retrieve import Get, GetConfig, GetReply
from edit import EditConfig, CopyConfig, DeleteConfig, Validate, Commit, DiscardChanges, ConfirmedCommit
from session import CloseSession, KillSession
from lock import Lock, Unlock, LockContext
#from subscribe import CreateSubscription

OPERATIONS = {
    'get': Get,
    'get-config': GetConfig,
    'edit-config': EditConfig,
    'copy-config': CopyConfig,
    'validate': Validate,
    'commit': Commit,
    'discard-changes': DiscardChanges,
    'delete-config': DeleteConfig,
    'lock': Lock,
    'unlock': Unlock,
    'close_session': CloseSession,
    'kill-session': KillSession,
}

__all__ = [
    'RPC',
    'RPCReply',
    'RPCError',
    'OPERATIONS',
    'Get',
    'GetConfig',
    'GetReply',
    'EditConfig',
    'CopyConfig',
    'Validate',
    'Commit',
    'ConfirmedCommit'
    'DiscardChanges',
    'DeleteConfig',
    'Lock',
    'Unlock',
    'LockContext',
    'CloseSession',
    'KillSession'
]
