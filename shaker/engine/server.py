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

import copy
import json
import os
import time
import uuid

from oslo_config import cfg
from oslo_log import log as logging
import yaml

from shaker.engine import config
from shaker.engine import deploy
from shaker.engine import executors as executors_classes
from shaker.engine import messaging
from shaker.engine import report
from shaker.engine import utils


LOG = logging.getLogger(__name__)


class Quorum(object):
    def __init__(self, message_queue, polling_interval):
        self.message_queue = message_queue
        self.polling_interval = polling_interval

    def wait_join(self, agent_ids):
        agent_ids = set(agent_ids)
        LOG.debug('Waiting for quorum of agents: %s', agent_ids)
        alive_agents = set()
        for message, reply_handler in self.message_queue:
            msg_agent_id = message.get('agent_id')

            if msg_agent_id not in agent_ids:
                reply_handler(dict(operation='none'))
                continue

            alive_agents.add(msg_agent_id)

            reply_handler(dict(operation='configure',
                               polling_interval=self.polling_interval))

            LOG.debug('Alive agents: %s', alive_agents)

            if alive_agents == agent_ids:
                LOG.info('All expected agents are alive')
                break

    def run_test_case(self, test_case):
        working_agents = set()
        replied_agents = set()
        result = {}

        start_at = int(time.time()) + self.polling_interval * 2

        for message, reply_handler in self.message_queue:
            agent_id = message.get('agent_id')
            operation = message.get('operation')

            reply = {'operation': 'none'}

            if agent_id not in test_case:
                reply_handler(reply)
                continue

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


def read_scenario():
    scenario_raw = utils.read_file(cfg.CONF.scenario)
    scenario = yaml.safe_load(scenario_raw)
    scenario['file_name'] = cfg.CONF.scenario
    LOG.debug('Scenario: %s', scenario)
    return scenario


def _extend_agents(agents):
    for agent in agents.values():
        if agent.get('slave_id'):
            agent['slave'] = copy.deepcopy(agents[agent['slave_id']])
        if agent.get('master_id'):
            agent['master'] = copy.deepcopy(agents[agent['master_id']])


def _pick_agents(agents, size):
    # slave agents do not execute any tests
    agents = [a for a in agents.values() if a.get('mode') != 'slave']

    if not size or size == 'full':
        yield agents
    elif size == 'linear_progression':
        for i in range(len(agents)):
            yield agents[:i + 1]
    elif size == 'quadratic_progression':
        n = len(agents)
        seq = [n]
        while n > 1:
            n //= 2
            seq.append(n)
        seq.reverse()
        for i in seq:
            yield agents[:i]


def execute(quorum, execution, agents):
    _extend_agents(agents)

    result = []

    for test in execution['tests']:
        LOG.debug('Running test %s on all agents', test)

        results_per_iteration = []
        for selected_agents in _pick_agents(agents, execution.get('size')):
            executors = dict((a['id'], executors_classes.get_executor(test, a))
                             for a in selected_agents)

            test_case_result = quorum.run_test_case(executors)
            values = test_case_result.values()
            for v in values:
                v['uuid'] = str(uuid.uuid4())
            results_per_iteration.append({
                'agents': selected_agents,
                'results_per_agent': values,
            })

        test['uuid'] = str(uuid.uuid4())
        result.append({
            'results_per_iteration': results_per_iteration,
            'definition': test,
        })

    LOG.info('Execution is done')
    return result


def main():
    utils.init_config_and_logging(
        config.COMMON_OPTS + config.OPENSTACK_OPTS + config.SERVER_OPTS +
        config.REPORT_OPTS
    )

    scenario = read_scenario()

    deployment = None
    agents = {}
    result = []

    try:
        deployment = deploy.Deployment(cfg.CONF.server_endpoint)

        if (cfg.CONF.os_username and cfg.CONF.os_password and
                cfg.CONF.os_tenant_name and cfg.CONF.os_auth_url):
            deployment.connect_to_openstack(
                cfg.CONF.os_username, cfg.CONF.os_password,
                cfg.CONF.os_tenant_name, cfg.CONF.os_auth_url,
                cfg.CONF.os_region_name, cfg.CONF.external_net,
                cfg.CONF.flavor_name, cfg.CONF.image_name)

        agents = deployment.deploy(scenario['deployment'],
                                   base_dir=os.path.dirname(cfg.CONF.scenario))
        LOG.debug('Deployed agents: %s', agents)

        if not agents:
            LOG.warning('No agents deployed.')
        else:
            message_queue = messaging.MessageQueue(cfg.CONF.server_endpoint)

            quorum = Quorum(message_queue, cfg.CONF.polling_interval)
            quorum.wait_join(set(agents.keys()))

            result = execute(quorum, scenario['execution'], agents)
            LOG.debug('Result: %s', result)
    except Exception as e:
        LOG.error('Error while executing scenario: %s', e)
    finally:
        if deployment:
            deployment.cleanup()

    report_data = dict(scenario=scenario,
                       agents=agents.values(),
                       result=result)
    if cfg.CONF.output:
        utils.write_file(json.dumps(report_data), cfg.CONF.output)

    report.generate_report(cfg.CONF.report_template, cfg.CONF.report,
                           report_data)


if __name__ == "__main__":
    main()
