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


class BaseOperation(object):
    def get_agent_join_timeout(self):
        return 0

    def get_active_agent_ids(self):
        pass

    def get_reply(self, agent_id, start_at):
        return {}

    def process_reply(self, agent_id, message):
        return {'status': 'ok'}

    def process_failure(self, agent_id):
        return {'status': 'lost'}


class JoinOperation(BaseOperation):
    def __init__(self, agent_ids, polling_interval, agent_join_timeout):
        super(JoinOperation, self).__init__()
        self.agent_ids = agent_ids
        self.polling_interval = polling_interval
        self.agent_join_timeout = agent_join_timeout

    def get_agent_join_timeout(self):
        return self.agent_join_timeout

    def get_active_agent_ids(self):
        return set(self.agent_ids)

    def get_reply(self, agent_id, start_at):
        return dict(operation='configure',
                    polling_interval=self.polling_interval,
                    expected_duration=0)


class ExecuteOperation(BaseOperation):
    def __init__(self, executors):
        super(ExecuteOperation, self).__init__()
        self.executors = executors

    def get_active_agent_ids(self):
        return set(self.executors.keys())

    def get_reply(self, agent_id, start_at):
        reply = dict(operation='execute',
                     start_at=start_at,
                     command=self.executors[agent_id].get_command(),
                     expected_duration=(self.executors[agent_id].
                                        get_expected_duration()))
        return reply

    def process_reply(self, agent_id, message):
        r = super(ExecuteOperation, self).process_reply(agent_id, message)
        r.update(self.executors[agent_id].process_reply(message))
        return r

    def process_failure(self, agent_id):
        r = super(ExecuteOperation, self).process_failure(agent_id)
        r.update(self.executors[agent_id].process_failure())
        return r


class Quorum(object):
    def __init__(self, message_queue, polling_interval, agent_loss_timeout,
                 agent_join_timeout):
        self.message_queue = message_queue
        self.polling_interval = polling_interval
        self.agent_loss_timeout = agent_loss_timeout
        self.agent_join_timeout = agent_join_timeout

    def _run(self, operation):
        current = operation.get_active_agent_ids()
        LOG.debug('Executing operation %s on agents: %s', operation, current)

        working = set()
        replied = set()
        result = {}

        start_at = time.time() + self.polling_interval * 2
        lives = dict((agent_id, start_at + operation.get_agent_join_timeout())
                     for agent_id in current)

        for message, reply_handler in self.message_queue:
            agent_id = message.get('agent_id')
            op = message.get('operation')
            reply = {'operation': 'none'}
            now = time.time()

            if agent_id in (current - replied):
                # message from a known not yet worked agent
                lives[agent_id] = (now + self.polling_interval * 2 +
                                   self.agent_loss_timeout)

                if op == 'poll':
                    reply = operation.get_reply(agent_id, start_at)
                    lives[agent_id] += reply.get('expected_duration')
                    working.add(agent_id)
                    LOG.debug('Working agents: %s', working)
                elif op == 'reply':
                    if agent_id in working:
                        result[agent_id] = operation.process_reply(
                            agent_id, message)
                        replied.add(agent_id)
                        LOG.debug('Replied agents: %s', replied)

            reply_handler(reply)

            lost = set(a for a, t in lives.items() if t < now) - replied
            if lost:
                LOG.debug('Lost agents: %s', lost)

            if replied | lost >= current:
                if lost:
                    LOG.warning('Lost agents: %s', lost)
                    # update result with info about lost agents
                    for agent_id in lost:
                        result[agent_id] = operation.process_failure(agent_id)

                LOG.info('Finished processing operation: %s', operation)
                break

        return result

    def join(self, agent_ids):
        LOG.debug('Waiting for quorum of agents: %s', agent_ids)
        return self._run(JoinOperation(agent_ids, self.polling_interval,
                                       self.agent_join_timeout))

    def execute(self, executors):
        return self._run(ExecuteOperation(executors))


def read_scenario():
    scenario_raw = utils.read_file(cfg.CONF.scenario)
    scenario = yaml.safe_load(scenario_raw)
    scenario['file_name'] = cfg.CONF.scenario
    LOG.debug('Scenario: %s', scenario)
    return scenario


def _extend_agents(agents_map):
    extended_agents = {}
    for agent in agents_map.values():
        extended = copy.deepcopy(agent)
        if agent.get('slave_id'):
            extended['slave'] = copy.deepcopy(agents_map[agent['slave_id']])
        if agent.get('master_id'):
            extended['master'] = copy.deepcopy(agents_map[agent['master_id']])
        extended_agents[agent['id']] = extended
    return extended_agents


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
    agents = _extend_agents(agents)

    result = []

    for test in execution['tests']:
        LOG.debug('Running test %s on all agents', test)

        results_per_iteration = []
        for selected_agents in _pick_agents(agents, execution.get('size')):
            executors = dict((a['id'], executors_classes.get_executor(test, a))
                             for a in selected_agents)

            execution_result = quorum.execute(executors)

            values = execution_result.values()
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

            quorum = Quorum(message_queue, cfg.CONF.polling_interval,
                            cfg.CONF.agent_loss_timeout,
                            cfg.CONF.agent_join_timeout)
            quorum.join(set(agents.keys()))

            result = execute(quorum, scenario['execution'], agents)
            LOG.debug('Result: %s', result)
    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            LOG.info('Caught SIGINT. Terminating')
        else:
            LOG.error('Error while executing scenario: %s', e)
    finally:
        if deployment:
            deployment.cleanup()

    report_data = dict(scenario=scenario,
                       agents=agents.values(),
                       result=result)
    if cfg.CONF.output:
        utils.write_file(json.dumps(report_data), cfg.CONF.output)

    report.generate_report(report_data, cfg.CONF.report_template,
                           cfg.CONF.report, cfg.CONF.subunit)


if __name__ == "__main__":
    main()
