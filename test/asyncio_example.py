import unittest
import sys
import asyncio
from mock import patch, MagicMock
from ncclient import operations
from ncclient import manager
from ncclient import async_manager

class TestAsyncioManager(object):

    def _mock_manager(self, async_mode=False):
        conn = manager.connect(host='hostname',
                               port=22,
                               username='user',
                               password='password',
                               timeout=30,
                               hostkey_verify=False,
                               allow_agent=False,
                               device_params={'name': 'junos'},
                               async_mode=async_mode,
                               raise_mode=operations.RaiseMode.ALL,
                               huge_tree=True,
                               )
        return conn

    @unittest.skipIf(sys.version_info.major == 2, "test not supported < python3")
    @patch('ncclient.transport.SSHSession')
    def test_async_mode(self, mock_ssh):
        m = MagicMock()
        mock_ssh.return_value = m
        conn = self._mock_manager(async_mode=True)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.multi_operations(loop, conn))

    async def multi_operations(self, loop, conn):
        # `conn.get()` is equivalent to self.mock_get_operation(), and so on.
        req = [
               self.mock_get_operation(),
               self.mock_get_config_operation(),
               self.mock_edit_config_operation(),
               self.mock_lock_operation(),
               self.mock_duplicate_lock_operation(),
              ]
        tasks = [loop.create_task(r) for r in req]
        return await asyncio.gather(*tasks)

    async def mock_get_operation(self):
        # mock the `get` operation
        await asyncio.sleep(1)
        return '<rpc-reply><data><root>This is `get` operations</root></data></rpc-reply>'

    async def mock_get_config_operation(self):
        # mock the `get-config` operation
        await asyncio.sleep(1)
        return '<rpc-reply><data><root>This is `get-config` operations</root></data></rpc-reply>'

    async def mock_edit_config_operation(self):
        # mock the `edit-config` operation
        await asyncio.sleep(1)
        return '<rpc-reply><ok/></rpc-reply>'

    async def mock_lock_operation(self):
        # mock the `lock` operation
        await asyncio.sleep(1)
        return '<rpc-reply><ok/></rpc-reply>'

    async def mock_duplicate_lock_operation(self):
        # mock the `lock` operation again
        await asyncio.sleep(1)
        return '<rpc-reply><rpc-error><error-message>Request resource already locked</error-message></rpc-error></rpc-reply>'
