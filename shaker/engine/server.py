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
import multiprocessing
import os
import uuid

from oslo_config import cfg
from oslo_log import log as logging

from shaker.agent import agent as agent_process
from shaker.engine import config
from shaker.engine import deploy
from shaker.engine import executors as executors_classes
from shaker.engine import messaging
from shaker.engine import quorum as quorum_pkg
from shaker.engine import report
from shaker.engine import utils


LOG = logging.getLogger(__name__)


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


def play_scenario(scenario):
    deployment = None
    output = dict(scenario=scenario)

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
        output['agents'] = agents
        LOG.debug('Deployed agents: %s', agents)

        if not agents:
            LOG.warning('No agents deployed.')
        else:
            message_queue = messaging.MessageQueue(cfg.CONF.server_endpoint)

            heartbeat = multiprocessing.Process(
                target=agent_process.work,
                kwargs=dict(agent_id='heartbeat',
                            endpoint=cfg.CONF.server_endpoint,
                            polling_interval=cfg.CONF.polling_interval))
            heartbeat.daemon = True
            heartbeat.start()

            quorum = quorum_pkg.Quorum(
                message_queue, cfg.CONF.polling_interval,
                cfg.CONF.agent_loss_timeout, cfg.CONF.agent_join_timeout)
            quorum.join(set(agents.keys()))

            execution_result = execute(quorum, scenario['execution'], agents)
            output['result'] = execution_result
    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            LOG.info('Caught SIGINT. Terminating')
        else:
            LOG.error('Error while executing scenario: %s', e)
    finally:
        if deployment:
            deployment.cleanup()

    return output


def main():
    utils.init_config_and_logging(
        config.COMMON_OPTS + config.OPENSTACK_OPTS + config.SERVER_OPTS +
        config.REPORT_OPTS
    )

    scenario = utils.read_yaml_file(cfg.CONF.scenario)
    scenario['file_name'] = cfg.CONF.scenario

    output = play_scenario(scenario)

    if cfg.CONF.output:
        utils.write_file(json.dumps(output), cfg.CONF.output)

    report.generate_report(output, cfg.CONF.report_template,
                           cfg.CONF.report, cfg.CONF.subunit)


if __name__ == "__main__":
    main()
