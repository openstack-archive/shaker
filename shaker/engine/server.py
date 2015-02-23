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

import time

from oslo_config import cfg
import yaml
import zmq

from shaker.engine import config
from shaker.engine import deploy
from shaker.engine import executors as executors_classes
from shaker.engine import report
from shaker.engine import utils
from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class Quorum(object):
    def __init__(self, message_queue):
        self.message_queue = message_queue

    def wait_join(self, agent_ids):
        LOG.debug('Waiting for quorum of agents: %s', agent_ids)
        alive_agents = set()
        for message, reply_handler in self.message_queue:
            agent_id = message.get('agent_id')
            alive_agents.add(agent_id)

            reply_handler(dict(operation='none'))

            LOG.debug('Alive agents: %s', alive_agents)

            if alive_agents >= agent_ids:
                LOG.info('All expected agents are alive')
                break

    def run_test_case(self, test_case):
        working_agents = set()
        replied_agents = set()
        result = {}

        start_at = int(time.time()) + 30  # schedule tasks in a 30 sec from now

        for message, reply_handler in self.message_queue:
            agent_id = message.get('agent_id')
            operation = message.get('operation')

            reply = {'operation': 'none'}
            if agent_id in test_case:
                # message from a known agent

                test = test_case[agent_id]

                if operation == 'poll':
                    reply = {
                        'operation': 'execute',
                        'start_at': start_at,
                        'command': test.get_command(),
                    }
                    working_agents.add(agent_id)
                elif operation == 'reply':
                    replied_agents.add(agent_id)
                    result[agent_id] = test.process_reply(message)

            reply_handler(reply)

            LOG.debug('Working agents: %s', working_agents)
            LOG.debug('Replied agents: %s', replied_agents)

            if replied_agents >= set(test_case.keys()):
                LOG.info('Received all replies for test case: %s', test_case)
                break

        return result


class MessageQueue(object):
    def __init__(self, endpoint):
        _, port = utils.split_address(endpoint)

        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % port)
        LOG.info('Listening on *:%s', port)

    def __iter__(self):
        try:
            while True:
                #  Wait for next request from client
                message = self.socket.recv_json()
                LOG.debug('Received request: %s', message)

                def reply_handler(reply_message):
                    self.socket.send_json(reply_message)

                try:
                    yield message, reply_handler
                except GeneratorExit:
                    break

        except BaseException as e:
            if not isinstance(e, KeyboardInterrupt):
                LOG.exception(e)
            raise


def read_scenario():
    scenario_raw = utils.read_file(cfg.CONF.scenario)
    scenario = yaml.safe_load(scenario_raw)
    scenario['file_name'] = cfg.CONF.scenario
    LOG.debug('Scenario: %s', scenario)
    return scenario


def _resolve_agent_ids(agents):
    id_to_agent = dict((ag['id'], ag) for ag in agents)
    for agent in agents:
        if agent.get('slave_id'):
            agent['slave'] = id_to_agent[agent['slave_id']]
        if agent.get('master_id'):
            agent['master'] = id_to_agent[agent['master_id']]


def _pick_agents(agents, size):
    # tests are executed on master agents only
    agents = [a for a in agents if a['mode'] == 'master']

    if not size or size == 'full':
        yield agents
    elif size == 'linear_progression':
        for i in range(len(agents)):
            yield agents[:i]
    elif size == 'quadratic_progression':
        n = len(agents)
        seq = [n]
        while n > 1:
            n /= 2
            seq.append(n)
        seq.reverse()
        for i in seq:
            yield agents[:i]


def execute(execution, agents):
    _resolve_agent_ids(agents)

    message_queue = MessageQueue(cfg.CONF.server_endpoint)

    quorum = Quorum(message_queue)
    quorum.wait_join(set(a['id'] for a in agents))

    result = []

    for test in execution['tests']:
        LOG.debug('Running test %s on all agents', test)

        results_per_iteration = []
        for selected_agents in _pick_agents(agents, execution.get('size')):
            executors = dict((a['id'], executors_classes.get_executor(test, a))
                             for a in selected_agents)

            test_case_result = quorum.run_test_case(executors)
            results_per_iteration.append({
                'agents': selected_agents,
                'results_per_agent': test_case_result.values(),
            })

        result.append({
            'results_per_iteration': results_per_iteration,
            'definition': test,
        })

    LOG.info('Execution is done')
    return result


def main():
    # init conf and logging
    conf = cfg.CONF
    conf.register_cli_opts(config.COMMON_OPTS)
    conf.register_cli_opts(config.OPENSTACK_OPTS)
    conf.register_cli_opts(config.SERVER_OPTS)
    conf.register_opts(config.COMMON_OPTS)
    conf.register_opts(config.OPENSTACK_OPTS)
    conf.register_opts(config.SERVER_OPTS)

    try:
        conf(project='shaker')
    except cfg.RequiredOptError as e:
        print('Error: %s' % e)
        conf.print_usage()
        exit(1)

    logging.setup('shaker')
    LOG.info('Logging enabled')

    scenario = read_scenario()
    deployment = deploy.Deployment(cfg.CONF.os_username,
                                   cfg.CONF.os_password,
                                   cfg.CONF.os_tenant_name,
                                   cfg.CONF.os_auth_url,
                                   cfg.CONF.os_region_name,
                                   cfg.CONF.server_endpoint,
                                   cfg.CONF.external_net,
                                   cfg.CONF.flavor_name,
                                   cfg.CONF.image_name)
    agents = deployment.deploy(scenario['deployment'])

    if not agents:
        LOG.info('No agents deployed. Exit.')
        return

    LOG.debug('Agents: %s', agents)

    result = execute(scenario['execution'], agents)
    LOG.debug('Result: %s', result)

    report.generate_report(cfg.CONF.report_template,
                           cfg.CONF.report,
                           dict(scenario=yaml.dump(scenario),
                                agents=agents,
                                result=result))

    deployment.cleanup()


if __name__ == "__main__":
    main()
