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
import re

from oslo_config import cfg
from oslo_log import log as logging

from shaker.engine import config
from shaker.engine import deploy
from shaker.engine import executors as executors_classes
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


def _make_test_title(test):
    s = test.get('title') or test.get('class')
    return re.sub(r'[^\x21-\x7e\x80-\xff]+', '_', s).lower()


def _pick_agents(agents, progression):
    # slave agents do not execute any tests
    agents = [a for a in agents.values() if a.get('mode') != 'slave']

    if not progression:
        yield agents
    elif progression in ['arithmetic', 'linear', 'linear_progression']:
        for i in range(len(agents)):
            yield agents[:i + 1]
    elif progression in ['geometric', 'quadratic', 'quadratic_progression']:
        n = len(agents)
        seq = [n]
        while n > 1:
            n //= 2
            seq.append(n)
        seq.reverse()
        for i in seq:
            yield agents[:i]


def execute(quorum, execution, agents):
    records = {}

    for test in execution['tests']:
        LOG.debug('Running test %s on all agents', test)
        test_title = _make_test_title(test)
        progression = execution.get('progression', execution.get('size'))

        for selected_agents in _pick_agents(agents, progression):
            executors = dict((a['id'], executors_classes.get_executor(test, a))
                             for a in selected_agents)

            execution_result = quorum.execute(executors)

            has_interrupted = False
            for agent_id, record in execution_result.items():
                record_id = utils.make_record_id()
                record.update(dict(
                    id=record_id,
                    agent=agent_id,
                    node=agents[agent_id].get('node'),
                    concurrency=len(selected_agents),
                    test=test_title,
                    executor=test.get('class'),
                    type='agent',
                ))
                records[record_id] = record
                has_interrupted |= record['status'] == 'interrupted'

            if has_interrupted:
                LOG.info('Execution is interrupted')
                return records

    LOG.info('Execution is done')
    return records


def play_scenario(scenario):
    deployment = None
    output = dict(scenario=scenario, records={}, agents={})
    output['tests'] = dict((_make_test_title(test), test)
                           for test in scenario['execution']['tests'])

    try:
        deployment = deploy.Deployment(cfg.CONF.server_endpoint)

        if (cfg.CONF.os_username and cfg.CONF.os_password and
                cfg.CONF.os_tenant_name and cfg.CONF.os_auth_url):
            deployment.connect_to_openstack(
                cfg.CONF.os_username, cfg.CONF.os_password,
                cfg.CONF.os_tenant_name, cfg.CONF.os_auth_url,
                cfg.CONF.os_region_name, cfg.CONF.external_net,
                cfg.CONF.flavor_name, cfg.CONF.image_name,
                cfg.CONF.os_cacert, cfg.CONF.os_insecure)

        base_dir = os.path.dirname(scenario['file_name'])
        agents = deployment.deploy(scenario['deployment'], base_dir=base_dir)

        agents = _extend_agents(agents)
        output['agents'] = agents
        LOG.debug('Deployed agents: %s', agents)

        if not agents:
            raise Exception('No agents deployed.')

        quorum = quorum_pkg.make_quorum(
            agents.keys(), cfg.CONF.server_endpoint,
            cfg.CONF.polling_interval, cfg.CONF.agent_loss_timeout,
            cfg.CONF.agent_join_timeout)

        output['records'] = execute(quorum, scenario['execution'], agents)

    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            LOG.info('Caught SIGINT. Terminating')
            record = dict(id=utils.make_record_id(), status='interrupted')
        else:
            error_msg = 'Error while executing scenario: %s' % e
            LOG.error(error_msg)
            LOG.exception(e)
            record = dict(id=utils.make_record_id(), status='error',
                          stderr=error_msg)
        output['records'][record['id']] = record
    finally:
        if deployment:
            deployment.cleanup()

    # extend every record with reference to scenario
    for record in output['records'].values():
        record['scenario'] = scenario['title']
    return output


def main():
    utils.init_config_and_logging(
        config.COMMON_OPTS + config.OPENSTACK_OPTS + config.SERVER_OPTS +
        config.REPORT_OPTS
    )

    output = dict(records={}, agents={}, scenarios={}, tests={})

    for scenario_param in [cfg.CONF.scenario]:
        LOG.debug('Processing scenario: %s', scenario_param)

        alias = '%s%s.yaml' % (config.SCENARIOS, scenario_param)
        packaged = utils.resolve_relative_path(alias)
        # use packaged scenario or fallback to full path
        scenario_file_name = packaged or scenario_param

        LOG.info('Play scenario: %s', scenario_file_name)
        scenario = utils.read_yaml_file(scenario_file_name)
        scenario['title'] = scenario.get('title') or scenario_file_name
        scenario['file_name'] = scenario_file_name

        play_output = play_scenario(scenario)

        output['scenarios'][scenario['title']] = play_output['scenario']
        output['records'].update(play_output['records'])
        output['agents'].update(play_output['agents'])
        output['tests'].update(play_output['tests'])

    if cfg.CONF.output:
        utils.write_file(json.dumps(output, indent=2), cfg.CONF.output)

    if cfg.CONF.no_report_on_error and 'error' in output:
        LOG.info('Skipped report generation due to errors and '
                 'no_report_on_error=True')
    else:
        report.generate_report(output, cfg.CONF.report_template,
                               cfg.CONF.report, cfg.CONF.subunit)


if __name__ == "__main__":
    main()
