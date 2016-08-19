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

import functools
from oslo_config import cfg
from oslo_log import log as logging

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


def _make_test_title(test, params=None):
    s = test.get('title') or test.get('class')
    if params:
        s += ' '.join([','.join(['%s=%s' % (k, v) for k, v in params.items()
                                if k != 'host'])])
    return re.sub(r'[^\x20-\x7e\x80-\xff]+', '_', s)


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


def run_test(records, quorum, test, agents, progression):

    LOG.debug('Running test %s on all agents', test)
    test_title = test['title']

    for selected_agents in _pick_agents(agents, progression):
        executors = dict((a['id'], executors_classes.get_executor(test, a))
                         for a in selected_agents)

        execution_result = quorum.execute(executors)

        has_interrupted = False
        for agent_id, record in execution_result.items():
            record_id = utils.make_record_id()
            node = agents[agent_id].get('node')
            if node == 'localhost':
                node = test.get('host')

            record.update(dict(
                id=record_id,
                agent=agent_id,
                node=node,
                concurrency=len(selected_agents),
                test=test_title,
                executor=test.get('class'),
                type='agent',
            ))
            records[record_id] = record
            has_interrupted |= record['status'] == 'interrupted'

        if has_interrupted:
            LOG.info('Execution is interrupted')
            return False

    return True


def _pick_tests(tests, matrix):
    matrix = matrix or {}
    for test in tests:
        for params in utils.algebraic_product(**matrix):
            parametrized_test = copy.deepcopy(test)
            parametrized_test.update(params)
            parametrized_test['title'] = _make_test_title(test, params)

            yield parametrized_test


def execute(output, quorum, execution, agents, matrix=None):
    progression = execution.get('progression', execution.get('size'))

    for test in _pick_tests(execution['tests'], matrix):
        output['tests'][test['title']] = test
        proceed = run_test(output['records'],
                           quorum, test, agents, progression)
        if not proceed:
            break  # propagate interruption signal

    LOG.info('Execution is done')


def _under_openstack():
    required = ['os_username', 'os_password', 'os_auth_url']
    for param in required:
        if param not in cfg.CONF:
            return False
    return True


def play_scenario(message_queue, scenario):
    deployment = None
    output = dict(scenarios={}, records={}, agents={}, tests={})
    output['scenarios'][scenario['title']] = scenario

    try:
        deployment = deploy.Deployment()

        if _under_openstack():
            openstack_params = utils.pack_openstack_params(cfg.CONF)
            try:
                deployment.connect_to_openstack(
                    openstack_params, cfg.CONF.flavor_name,
                    cfg.CONF.image_name, cfg.CONF.external_net,
                    cfg.CONF.dns_nameservers)
            except Exception as e:
                LOG.warning('Failed to connect to OpenStack: %s. Please '
                            'verify parameters: %s', e, openstack_params)

        base_dir = os.path.dirname(scenario['file_name'])
        scenario_deployment = scenario.get('deployment', {})
        server_endpoint = (cfg.CONF.server_endpoint
                           if 'server_endpoint' in cfg.CONF else None)

        agents = deployment.deploy(scenario_deployment, base_dir=base_dir,
                                   server_endpoint=server_endpoint)

        agents = _extend_agents(agents)
        output['agents'] = agents
        LOG.debug('Deployed agents: %s', agents)

        if not agents:
            raise Exception('No agents deployed.')

        if scenario_deployment:
            quorum = quorum_pkg.make_quorum(
                agents.keys(), message_queue,
                cfg.CONF.polling_interval, cfg.CONF.agent_loss_timeout,
                cfg.CONF.agent_join_timeout)
        else:
            # local
            quorum = quorum_pkg.make_local_quorum()

        matrix = cfg.CONF.matrix if 'matrix' in cfg.CONF else None
        if matrix:
            scenario['matrix'] = matrix

        execute(output, quorum, scenario['execution'], agents, matrix)

    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            LOG.info('Caught SIGINT. Terminating')
            record = dict(id=utils.make_record_id(), status='interrupted')
        else:
            error_msg = 'Error while executing scenario: %s' % e
            LOG.error(error_msg, exc_info=True)
            record = dict(id=utils.make_record_id(), status='error',
                          stderr=error_msg)
        output['records'][record['id']] = record
    finally:
        if deployment:
            try:
                deployment.cleanup()
            except Exception as e:
                LOG.error('Failed to cleanup the deployment: %s', e,
                          exc_info=True)

    # extend every record with reference to scenario
    for record in output['records'].values():
        record['scenario'] = scenario['title']
    return output


def read_scenario(scenario_name):
    alias_base = scenario_name
    if alias_base[:11] == 'networking/':  # backward compatibility
        LOG.warning('Scenarios from networking/ are moved to openstack/')
        alias_base = 'openstack/' + alias_base[11:]

    alias = '%s%s.yaml' % (config.SCENARIOS, alias_base)
    packaged = utils.resolve_relative_path(alias)

    # use packaged scenario or fallback to full path
    scenario_file_name = packaged or scenario_name
    LOG.debug('Scenario %s is resolved to %s', scenario_name,
              scenario_file_name)

    scenario = utils.read_yaml_file(scenario_file_name)

    schema = utils.read_yaml_file(utils.resolve_relative_path(
        '%s%s.yaml' % (config.SCHEMAS, 'scenario')))
    utils.validate_yaml(scenario, schema)

    scenario['title'] = scenario.get('title') or scenario_file_name
    scenario['file_name'] = scenario_file_name

    return scenario


def act():
    outputs = []

    message_queue = None
    if 'server_endpoint' in cfg.CONF:
        message_queue = messaging.MessageQueue(cfg.CONF.server_endpoint)

    artifacts_dir = cfg.CONF.artifacts_dir
    if artifacts_dir:
        utils.mkdir_tree(artifacts_dir)

    for scenario_name in cfg.CONF.scenario:
        LOG.info('Play scenario: %s', scenario_name)

        scenario = read_scenario(scenario_name)

        play_output = play_scenario(message_queue, scenario)
        outputs.append(copy.deepcopy(play_output))

        # if requested make separate reports
        if artifacts_dir:
            prefix = utils.strict(scenario_name)
            report_name_fn = functools.partial(
                utils.join_folder_prefix_ext, artifacts_dir, prefix)
            utils.write_file(json.dumps(play_output, indent=2),
                             report_name_fn('json'))
            report.generate_report(
                play_output, cfg.CONF.report_template, report_name_fn('html'),
                report_name_fn('subunit'), report_name_fn())

    LOG.info('Generating aggregated report')
    aggregated = utils.merge_dicts(outputs)

    utils.write_file(json.dumps(aggregated, indent=2), cfg.CONF.output)
    LOG.info('Raw output is stored to: %s', cfg.CONF.output)

    report.generate_report(aggregated, cfg.CONF.report_template,
                           cfg.CONF.report, cfg.CONF.subunit, cfg.CONF.book)


def main():
    utils.init_config_and_logging(
        config.COMMON_OPTS + config.OPENSTACK_OPTS + config.SERVER_OPTS +
        config.REPORT_OPTS
    )

    act()


if __name__ == "__main__":
    main()
