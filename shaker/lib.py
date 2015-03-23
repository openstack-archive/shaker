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

from oslo_log import log as logging

from shaker.engine import messaging
from shaker.engine import server


LOG = logging.getLogger(__name__)


class Shaker(object):
    """How to use Shaker as library

    shaker = Shaker('127.0.0.1:5999', ['the-agent'])
    res = shaker.run_program('the-agent', 'ls -al')
    """
    def __init__(self, server_endpoint, agent_ids, polling_interval=1):
        self.server_endpoint = server_endpoint
        self.polling_interval = polling_interval

        message_queue = messaging.MessageQueue(self.server_endpoint)
        self.quorum = server.Quorum(message_queue, self.polling_interval)
        self.quorum.wait_join(agent_ids)

    def _run(self, agent_id, item):
        agents = dict([(agent_id, dict(id=agent_id, mode='alone'))])

        test = {'class': 'shell'}
        test.update(item)

        execution = {'tests': [test]}
        execution_result = server.execute(self.quorum, execution, agents)

        results_per_iteration = execution_result[0]['results_per_iteration']
        results_per_agent = results_per_iteration[0]['results_per_agent']
        return dict((s['agent']['id'], s) for s in results_per_agent)

    def run_program(self, agent_id, program):
        return self._run(agent_id, {'program': program})

    def run_script(self, agent_id, script):
        return self._run(agent_id, {'script': script})
