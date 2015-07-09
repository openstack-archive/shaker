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

import functools

import mock
import testtools

from shaker.engine.executors import base as base_executor
from shaker.engine import quorum as quorum_pkg


STEP = 10  # polling interval
LOSS_TIMEOUT = 60
JOIN_TIMEOUT = 600

make_quorum = functools.partial(quorum_pkg.Quorum, polling_interval=STEP,
                                agent_loss_timeout=LOSS_TIMEOUT,
                                agent_join_timeout=JOIN_TIMEOUT)


class DummyExecutor(base_executor.BaseExecutor):
    def __init__(self, duration=STEP):
        super(DummyExecutor, self).__init__({}, None)
        self.duration = duration

    def get_expected_duration(self):
        return self.duration

    def process_reply(self, message):
        return super(DummyExecutor, self).process_reply(message)

    def get_command(self):
        return 'RUN'


class TestQuorum(testtools.TestCase):

    def setUp(self):
        self.mock_time = mock.Mock()
        self._mock_patch = mock.patch('time.time', self.mock_time)
        self._mock_patch.start()
        return super(TestQuorum, self).setUp()

    def tearDown(self):
        self._mock_patch.stop()
        return super(TestQuorum, self).tearDown()

    def _reply(self, expected):
        def reply_handler(reply_message):
            self.assertEqual(expected, reply_message)

        return reply_handler

    def _message_queue_gen(self, event_stream, fail_at_end=True):
        for event in event_stream:
            self.mock_time.return_value = event['time']
            yield (event['msg'], self._reply(event['reply']))

    def test_poll_reply(self):
        self.mock_time.return_value = 0
        event_stream = [
            dict(msg=dict(operation='poll', agent_id='alpha'),
                 reply=dict(operation='execute', command='RUN',
                            start_at=STEP * 2, expected_duration=STEP),
                 time=1),
            dict(msg=dict(operation='reply', agent_id='alpha'),
                 reply=dict(operation='none'),
                 time=20),
        ]

        quorum = make_quorum(self._message_queue_gen(event_stream))
        test_case = {
            'alpha': DummyExecutor()
        }
        result = quorum.execute(test_case)
        self.assertEqual(result.keys(), test_case.keys())

    def test_poll_reply_unknown_agent_ignored(self):
        self.mock_time.return_value = 0
        event_stream = [
            dict(msg=dict(operation='poll', agent_id='alpha'),
                 reply=dict(operation='execute', command='RUN',
                            start_at=STEP * 2, expected_duration=STEP),
                 time=1),
            dict(msg=dict(operation='reply', agent_id='beta'),
                 reply=dict(operation='none'),
                 time=20),
            dict(msg=dict(operation='reply', agent_id='alpha'),
                 reply=dict(operation='none'),
                 time=20),
        ]

        quorum = make_quorum(self._message_queue_gen(event_stream))
        test_case = {
            'alpha': DummyExecutor()
        }
        result = quorum.execute(test_case)
        self.assertEqual(result.keys(), test_case.keys())

    def test_lost_agent(self):
        self.mock_time.return_value = 0
        event_stream = [
            dict(msg=dict(operation='poll', agent_id='alpha'),
                 reply=dict(operation='execute', command='RUN',
                            start_at=STEP * 2, expected_duration=STEP),
                 time=1),
            dict(msg=dict(operation='reply',
                          agent_id=quorum_pkg.HEARTBEAT_AGENT),
                 reply=dict(operation='none'),
                 time=STEP * 10),
        ]

        quorum = make_quorum(self._message_queue_gen(event_stream))
        test_case = {
            'alpha': DummyExecutor()
        }
        result = quorum.execute(test_case)
        self.assertEqual(result.keys(), test_case.keys())
        self.assertEqual('lost', result['alpha']['status'])

    def test_agent_loss_timeout(self):
        """Tests that agent is not marked as lost during loss-timeout."""
        self.mock_time.return_value = 0
        event_stream = [
            dict(msg=dict(operation='poll', agent_id='_lost'),
                 reply=dict(operation='execute', command='RUN',
                            start_at=STEP * 2, expected_duration=STEP),
                 time=1),
            dict(msg=dict(operation='reply',
                          agent_id=quorum_pkg.HEARTBEAT_AGENT),
                 reply=dict(operation='none'),
                 time=LOSS_TIMEOUT),
            dict(msg=dict(operation='reply', agent_id='_lost'),
                 reply=dict(operation='none'),
                 time=LOSS_TIMEOUT),
        ]

        quorum = make_quorum(self._message_queue_gen(event_stream))
        test_case = {
            '_lost': DummyExecutor()
        }
        result = quorum.execute(test_case)
        self.assertEqual(result.keys(), test_case.keys())
        self.assertEqual('ok', result['_lost']['status'])

    def test_good_and_lost(self):
        self.mock_time.return_value = 0
        event_stream = [
            dict(msg=dict(operation='poll', agent_id='_lost'),
                 reply=dict(operation='execute', command='RUN',
                            start_at=STEP * 2, expected_duration=STEP),
                 time=1),
            dict(msg=dict(operation='poll', agent_id='beta'),
                 reply=dict(operation='execute', command='RUN',
                            start_at=STEP * 2, expected_duration=STEP),
                 time=2),
            dict(msg=dict(operation='reply', agent_id='beta'),
                 reply=dict(operation='none'),
                 time=20),
            dict(msg=dict(operation='reply',
                          agent_id=quorum_pkg.HEARTBEAT_AGENT),
                 reply=dict(operation='none'),
                 time=STEP * 10),
        ]

        quorum = make_quorum(self._message_queue_gen(event_stream))
        test_case = {
            '_lost': DummyExecutor(),
            'beta': DummyExecutor(),
        }
        result = quorum.execute(test_case)
        self.assertEqual(set(result.keys()), set(test_case.keys()))
        self.assertEqual('lost', result['_lost']['status'])
        self.assertEqual('ok', result['beta']['status'])

    def test_wait_agentexecutening_long_test(self):
        self.mock_time.return_value = 0
        event_stream = [
            dict(msg=dict(operation='poll', agent_id='alpha'),
                 reply=dict(operation='execute', command='RUN',
                            start_at=STEP * 2, expected_duration=STEP * 9),
                 time=1),
            dict(msg=dict(operation='reply',
                          agent_id=quorum_pkg.HEARTBEAT_AGENT),
                 reply=dict(operation='none'),
                 time=STEP * 4),
            dict(msg=dict(operation='reply', agent_id='alpha'),
                 reply=dict(operation='none'),
                 time=STEP * 9),
        ]

        quorum = make_quorum(self._message_queue_gen(event_stream))
        test_case = {
            'alpha': DummyExecutor(duration=STEP * 9)
        }
        result = quorum.execute(test_case)
        self.assertEqual(result.keys(), test_case.keys())
        self.assertEqual('ok', result['alpha']['status'])

    def test_good_and_interrupted(self):
        self.mock_time.return_value = 0
        event_stream = [
            dict(msg=dict(operation='poll', agent_id='alpha'),
                 reply=dict(operation='execute', command='RUN',
                            start_at=STEP * 2, expected_duration=STEP),
                 time=1),
            dict(msg=dict(operation='poll', agent_id='beta'),
                 reply=dict(operation='execute', command='RUN',
                            start_at=STEP * 2, expected_duration=STEP),
                 time=2),
            dict(msg=dict(operation='reply', agent_id='beta'),
                 reply=dict(operation='none'),
                 time=20),
        ]

        quorum = make_quorum(self._message_queue_gen(event_stream,
                                                     fail_at_end=False))
        test_case = {
            'alpha': DummyExecutor(),
            'beta': DummyExecutor(),
        }
        result = quorum.execute(test_case)
        self.assertEqual(result.keys(), test_case.keys())
        self.assertEqual('interrupted', result['alpha']['status'])
        self.assertEqual('ok', result['beta']['status'])

    def test_join_succeed(self):
        self.mock_time.return_value = 0
        event_stream = [
            dict(msg=dict(operation='poll', agent_id='alpha'),
                 reply=dict(operation='configure', polling_interval=STEP,
                            expected_duration=0),
                 time=STEP),
            dict(msg=dict(operation='reply', agent_id='alpha'),
                 reply=dict(operation='none'),
                 time=STEP * 2),
            dict(msg=dict(operation='poll',
                          agent_id=quorum_pkg.HEARTBEAT_AGENT),
                 reply=dict(operation='none'),
                 time=STEP * 2),
        ]

        quorum = make_quorum(self._message_queue_gen(event_stream))
        result = quorum.join(['alpha'])
        lost = [agent_id for agent_id, r in result.items()
                if r['status'] == 'lost']
        self.assertEqual([], lost)

    def test_join_failed(self):
        self.mock_time.return_value = 0
        event_stream = [
            dict(msg=dict(operation='poll', agent_id='_lost'),
                 reply=dict(operation='configure', polling_interval=STEP,
                            expected_duration=0),
                 time=STEP),
            dict(msg=dict(operation='reply',
                          agent_id=quorum_pkg.HEARTBEAT_AGENT),
                 reply=dict(operation='none'),
                 time=JOIN_TIMEOUT + STEP * 2),
        ]

        quorum = make_quorum(self._message_queue_gen(event_stream))
        result = quorum.join(['_lost'])
        lost = [agent_id for agent_id, r in result.items()
                if r['status'] == 'lost']
        self.assertEqual(['_lost'], lost)
