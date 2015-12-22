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

from shaker.engine import quorum
from shaker.engine import server


LOG = logging.getLogger(__name__)


class Shaker(object):
    """How to use Shaker as library

>>> from shaker import lib
>>> shaker = lib.Shaker('127.0.0.1:5999')
>>> shaker.run_program('the-agent', 'date')
{
    'status': 'ok',
    'stdout': 'Thu Apr 23 13:09:08 EAT 2015\n',
    'agent': 'the-agent',
    'command': {'data': 'date', 'type': 'program'},
    'stderr': u'',
    'executor': 'shell',
    'test': 'shell',
    'type': 'agent',
    'id': '3a7c3d97-45f1-43ba-8460-2e37e679e3d5'
}
    """
    def __init__(self, server_endpoint, agent_ids=None, polling_interval=1,
                 agent_loss_timeout=60, agent_join_timeout=600):
        self.quorum = quorum.make_quorum(
            agent_ids or [], server_endpoint, polling_interval,
            agent_loss_timeout, agent_join_timeout)

    def _run(self, agent_id, item):
        self.quorum.join({agent_id})
        agents = dict([(agent_id, dict(id=agent_id, mode='alone'))])

        test = {'class': 'shell'}
        test.update(item)

        execution = {'tests': [test]}
        output = dict(records={}, agents={}, tests={})
        server.execute(output, self.quorum, execution, agents)

        return list(output['records'].values())[0]

    def run_program(self, agent_id, program):
        return self._run(agent_id, {'program': program})

    def run_script(self, agent_id, script):
        return self._run(agent_id, {'script': script})
