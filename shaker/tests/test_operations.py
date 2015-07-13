# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import testtools

from shaker.engine.executors import base
from shaker.engine import quorum


class TestOperations(testtools.TestCase):

    def test_execute_operation_process_reply(self):
        executor = mock.MagicMock()
        executor.process_reply = mock.Mock(return_value={'samples': []})

        agent_id = 'the-agent'
        ex = quorum.ExecuteOperation({agent_id: executor})

        message = {
            'stdout': 'foo',
            'stderr': '',
        }
        reply = ex.process_reply(agent_id, message)

        expected = {
            'status': 'ok',
            'samples': [],
        }
        executor.process_reply.assert_called_once_with(message)
        self.assertEqual(expected, reply)

    def test_execute_operation_process_reply_with_error(self):
        executor = mock.MagicMock()
        executor.process_reply = mock.Mock(
            side_effect=base.ExecutorException({'stderr': 'sad'}, 'Error!'))

        agent_id = 'the-agent'
        ex = quorum.ExecuteOperation({agent_id: executor})

        message = {
            'stdout': 'foo',
            'stderr': '',
        }
        reply = ex.process_reply(agent_id, message)

        expected = {
            'status': 'error',
            'stderr': 'sad',
            'info': 'Error!'
        }
        executor.process_reply.assert_called_once_with(message)
        self.assertDictContainsSubset(expected, reply)

    def test_execute_operation_process_reply_with_unhandled_exception(self):
        executor = mock.MagicMock()
        executor.process_reply = mock.Mock(
            side_effect=Exception('Boom!'))

        agent_id = 'the-agent'
        ex = quorum.ExecuteOperation({agent_id: executor})

        message = {}
        reply = ex.process_reply(agent_id, message)

        expected = {
            'status': 'error',
            'info': 'Boom!'
        }
        executor.process_reply.assert_called_once_with(message)
        self.assertDictContainsSubset(expected, reply)
