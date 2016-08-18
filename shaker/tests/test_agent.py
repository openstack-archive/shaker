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

from shaker.agent import agent


class TestAgent(testtools.TestCase):

    @mock.patch('shaker.agent.agent.sleep')
    def test_work_act_idle(self, mock_sleep):
        agent_id = 'the-agent'
        polling_interval = 10
        agent_config = dict(polling_interval=polling_interval)

        mock_socket = mock.Mock()
        mock_socket.recv_json.side_effect = [{}]

        agent.work_act(mock_socket, agent_id, agent_config)

        mock_sleep.assert_called_once_with(polling_interval)
        mock_socket.send_json.assert_called_once_with(
            dict(operation='poll', agent_id=agent_id))
        mock_socket.recv_json.assert_called_once_with()

    @mock.patch('shaker.agent.agent.sleep')
    @mock.patch('shaker.agent.agent.run_command')
    def test_work_act_execute(self, mock_run_command, mock_sleep):
        agent_id = 'the-agent'
        polling_interval = 10
        agent_config = dict(polling_interval=polling_interval)

        mock_socket = mock.Mock()
        mock_socket.recv_json.side_effect = [
            dict(operation='execute'), dict(),
        ]
        execute_result = {'res': 'data'}
        mock_run_command.return_value = execute_result

        agent.work_act(mock_socket, agent_id, agent_config)

        mock_sleep.assert_called_once_with(polling_interval)

        mock_socket.send_json.assert_has_calls([
            mock.call(dict(operation='poll', agent_id=agent_id)),
            mock.call(dict(operation='reply', agent_id=agent_id, res='data')),
        ])

    @mock.patch('shaker.agent.agent.sleep')
    @mock.patch('shaker.agent.agent.time_now')
    @mock.patch('shaker.agent.agent.run_command')
    def test_work_act_schedule(self, mock_run_command, mock_now, mock_sleep):
        agent_id = 'the-agent'
        polling_interval = 10
        start_at = 1234
        now = 1230
        agent_config = dict(polling_interval=polling_interval)

        mock_socket = mock.Mock()
        mock_socket.recv_json.side_effect = [
            dict(operation='execute', start_at=start_at), dict(),
        ]
        execute_result = {'res': 'data'}
        mock_run_command.return_value = execute_result

        mock_now.return_value = now

        agent.work_act(mock_socket, agent_id, agent_config)

        mock_sleep.assert_has_calls([
            mock.call(start_at - now),
            mock.call(polling_interval),
        ])

        mock_socket.send_json.assert_has_calls([
            mock.call(dict(operation='poll', agent_id=agent_id)),
            mock.call(dict(operation='reply', agent_id=agent_id, res='data')),
        ])

    @mock.patch('shaker.agent.agent.sleep')
    @mock.patch('shaker.agent.agent.run_command')
    def test_work_act_configure(self, mock_run_command, mock_sleep):
        agent_id = 'the-agent'
        new_polling_interval = 2
        agent_config = dict(polling_interval=10)

        mock_socket = mock.Mock()
        mock_socket.recv_json.side_effect = [
            dict(operation='configure', polling_interval=new_polling_interval),
            dict(),
        ]

        agent.work_act(mock_socket, agent_id, agent_config)

        mock_sleep.assert_has_calls([
            mock.call(new_polling_interval),
        ])

        mock_socket.send_json.assert_has_calls([
            mock.call(dict(operation='poll', agent_id=agent_id)),
            mock.call(dict(operation='reply', agent_id=agent_id)),
        ])
