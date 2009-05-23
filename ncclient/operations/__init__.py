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

from errors import OperationError, TimeoutExpiredError, MissingCapabilityError
from rpc import RPC, RPCReply, RPCError

# rfc4741 ops
from retrieve import Get, GetConfig, GetReply
from edit import EditConfig, CopyConfig, DeleteConfig, Validate, Commit, DiscardChanges
from session import CloseSession, KillSession
from lock import Lock, Unlock, LockContext
# others...
from flowmon import PoweroffMachine, RebootMachine

INDEX = {
    'get': Get,
    'get_config': GetConfig,
    'edit_config': EditConfig,
    'copy_config': CopyConfig,
    'validate': Validate,
    'commit': Commit,
    'discard_changes': DiscardChanges,
    'delete_config': DeleteConfig,
    'lock': Lock,
    'unlock': Unlock,
    'close_session': CloseSession,
    'kill_session': KillSession,
    'poweroff_machine': PoweroffMachine,
    'reboot_machine': RebootMachine
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
    'DiscardChanges',
    'DeleteConfig',
    'Lock',
    'Unlock',
    'PoweroffMachine',
    'RebootMachine',
    'LockContext',
    'CloseSession',
    'KillSession',
    'OperationError',
    'TimeoutExpiredError',
    'MissingCapabilityError'
]
