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
import json
import sys

import jinja2
from oslo_config import cfg
from oslo_log import log as logging
from subunit import v2 as subunit_v2
import yaml

from shaker.engine import aggregators
from shaker.engine import config
from shaker.engine import utils


LOG = logging.getLogger(__name__)


def calculate_stats(data):
    for test_result in data['result']:
        aggregator = aggregators.get_aggregator(test_result['definition'])

        for iteration_result in test_result['results_per_iteration']:
            for agent_result in iteration_result['results_per_agent']:
                aggregator.agent_summary(agent_result)

            aggregator.iteration_summary(iteration_result)

        aggregator.test_summary(test_result)


def verify_sla(data, subunit_filename):
    if not subunit_filename:
        return

    fd = open(subunit_filename, 'w')
    output = subunit_v2.StreamResultToBytes(fd)

    for test_result in data['result']:
        sla = test_result['definition'].get('sla')
        if not sla:
            continue

        test_name = (test_result['definition'].get('title') or
                     test_result['definition'].get('class'))
        for iteration_result in test_result['results_per_iteration']:
            for agent_result in iteration_result['results_per_agent']:
                stats = agent_result['stats']

                for k, params in sla.items():
                    if k not in stats:
                        LOG.warning('SLA parameter %s not found', k)
                        continue
                    for p, value in params.items():
                        if p not in stats[k]:
                            LOG.warning('SLA parameter %s:%s not found', k, p)
                            continue

                        sla_name = '%s.%s.%s.%s.%s' % (
                            test_name,
                            len(iteration_result['results_per_agent']),
                            agent_result['agent']['id'],
                            k, p)
                        output.startTestRun()
                        status = value < stats[k][p]

                        if value < stats[k][p]:
                            LOG.debug('SLA %s OK', sla_name)
                        else:
                            LOG.debug('SLA %s FAILED', sla_name)

                        output.status(
                            test_id=sla_name,
                            file_name='results',
                            mime_type='text/plain; charset="utf8"',
                            eof=True,
                            file_bytes=yaml.safe_dump(
                                stats[k], default_flow_style=False))

                        output.status(
                            test_id=sla_name,
                            test_status='success' if status else 'fail')
                        output.stopTestRun()

    fd.close()


def generate_report(data, report_template, report_filename, subunit_filename):
    LOG.debug('Generating report, template: %s, output: %s',
              report_template, report_filename or 'stdout')

    calculate_stats(data)
    verify_sla(data, subunit_filename)

    # add more filters to jinja
    jinja_env = jinja2.Environment()
    jinja_env.filters['json'] = json.dumps
    jinja_env.filters['yaml'] = functools.partial(yaml.safe_dump, indent=2,
                                                  default_flow_style=False)

    template = utils.read_file(report_template)
    compiled_template = jinja_env.from_string(template)
    rendered_template = compiled_template.render(dict(report=data))

    if report_filename:
        fd = open(report_filename, 'w')
    else:
        fd = sys.stdout

    fd.write(rendered_template)
    fd.close()
    LOG.info('Report generated')


def main():
    utils.init_config_and_logging(config.REPORT_OPTS + config.INPUT_OPTS)

    LOG.debug('Reading JSON data from: %s', cfg.CONF.input)
    report_data = json.loads(utils.read_file(cfg.CONF.input))

    generate_report(report_data, cfg.CONF.report_template, cfg.CONF.report,
                    cfg.CONF.subunit)


if __name__ == "__main__":
    main()
