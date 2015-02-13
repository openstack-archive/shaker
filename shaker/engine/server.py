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
from shaker.engine import utils
from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class Quorum(object):
    def __init__(self, message_queue, agents):
        self.message_queue = message_queue
        self.agents = agents

        self.agent_ids = set(a['id'] for a in agents)

    def wait_join(self):
        alive_agents = set()
        for message, reply_handler in self.message_queue:
            agent_id = message.get('agent_id')
            alive_agents.add(agent_id)

            reply_handler(dict(operation='none'))

            LOG.debug('Alive agents: %s', alive_agents)

            if alive_agents >= self.agent_ids:
                LOG.info('All expected agents are alive')
                break

    def run_test_case(self, test_case):
        working_agents = set()
        replied_agents = set()

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
                    test.process_reply(message)

            reply_handler(reply)

            LOG.debug('Working agents: %s', working_agents)
            LOG.debug('Replied agents: %s', replied_agents)

            if replied_agents >= set(test_case.keys()):
                LOG.info('Received all replies for test case: %s', test_case)
                break


class TestCase(object):
    def __init__(self):
        super(TestCase, self).__init__()

    def to_command(self):
        pass

    def store_result(self):
        pass


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
    LOG.debug('Scenario: %s', scenario)
    return scenario


def execute(execution, agents):
    message_queue = MessageQueue(cfg.CONF.server_endpoint)

    LOG.debug('Creating quorum of agents: %s', agents)
    quorum = Quorum(message_queue, agents.values())

    LOG.debug('Waiting for quorum of agents')
    quorum.wait_join()

    for test_definition in execution['tests']:
        LOG.debug('Running test %s on all agents', test_definition)

        executors = dict()
        for agent_id, agent in agents.items():
            if agent['mode'] == 'master':
                # tests are executed on master agents only
                executors[agent_id] = executors_classes.get_executor(
                    test_definition, agent)

        quorum.run_test_case(executors)

    LOG.info('Done')


def main():
    # init conf and logging
    conf = cfg.CONF
    conf.register_cli_opts(config.COMMON_OPTS)
    conf.register_cli_opts(config.SERVER_OPTS)
    conf.register_opts(config.COMMON_OPTS)
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
                                   cfg.CONF.server_endpoint)
    agents = deployment.deploy(scenario['deployment'])

    if not agents:
        LOG.warning('No agents specified. Exiting.')
        return

    LOG.debug('Agents: %s', agents)

    execute(scenario['execution'], agents)
    deployment.cleanup()


if __name__ == "__main__":
    main()
