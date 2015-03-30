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

import collections
import functools
import json

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


SLARecord = collections.namedtuple('SLARecord',
                                   ['sla', 'status', 'location', 'stats'])


def _verify_stats_against_sla(sla, stats, location):
    res = []
    for term in sla:
        status = utils.eval_expr(term, stats)
        sla_record = SLARecord(sla=term, status=status,
                               location=location, stats=stats)
        res.append(sla_record)
        LOG.debug('SLA: %s', sla_record)
    return res


def verify_sla(data):
    res = []
    for test_result in data['result']:
        test_name = (test_result['definition'].get('title') or
                     test_result['definition'].get('class'))
        sla = test_result['definition'].get('sla')
        if not sla:
            continue

        for iteration_result in test_result['results_per_iteration']:
            size = str(len(iteration_result['results_per_agent']))

            sla_info = _verify_stats_against_sla(
                sla, iteration_result['stats'],
                '%s.%s' % (test_name, size))
            res += sla_info
            iteration_result['sla_info'] = sla_info

            for agent_result in iteration_result['results_per_agent']:
                agent_id = agent_result['agent']['id']

                sla_info = _verify_stats_against_sla(
                    sla, agent_result['stats'],
                    '%s.%s.%s' % (test_name, size, agent_id))
                res += sla_info
                agent_result['sla_info'] = sla_info

    return res


def save_to_subunit(sla_res, subunit_filename):
    LOG.debug('Writing subunit stream to: %s', subunit_filename)
    fd = None
    try:
        fd = open(subunit_filename, 'w')
        output = subunit_v2.StreamResultToBytes(fd)

        for item in sla_res:
            output.startTestRun()
            test_id = item.location + ':' + item.sla

            if not item.status:
                output.status(test_id=test_id, file_name='results',
                              mime_type='text/plain; charset="utf8"', eof=True,
                              file_bytes=yaml.safe_dump(
                                  item.stats, default_flow_style=False))

            output.status(test_id=test_id,
                          test_status='success' if item.status else 'fail')
            output.stopTestRun()

        LOG.info('Subunit stream saved to: %s', subunit_filename)
    except IOError as e:
        LOG.error('Error writing subunit stream: %s', e)
    finally:
        if fd:
            fd.close()


def generate_report(data, report_template, report_filename, subunit_filename):
    LOG.debug('Generating report, template: %s, output: %s',
              report_template, report_filename or '<dummy>')

    calculate_stats(data)
    sla_res = verify_sla(data)

    if subunit_filename:
        save_to_subunit(sla_res, subunit_filename)

    # add more filters to jinja
    jinja_env = jinja2.Environment()
    jinja_env.filters['json'] = json.dumps
    jinja_env.filters['yaml'] = functools.partial(yaml.safe_dump, indent=2,
                                                  default_flow_style=False)

    template = utils.read_file(report_template)
    compiled_template = jinja_env.from_string(template)
    rendered_template = compiled_template.render(dict(report=data))

    if report_filename:
        LOG.debug('Writing report to: %s', report_filename)
        try:
            utils.write_file(rendered_template, report_filename)
            LOG.info('Report saved to: %s', report_filename)
        except IOError as e:
            LOG.error('Failed to write report file: %s', e)


def main():
    utils.init_config_and_logging(config.REPORT_OPTS + config.INPUT_OPTS)

    LOG.debug('Reading JSON data from: %s', cfg.CONF.input)
    report_data = json.loads(utils.read_file(cfg.CONF.input))

    generate_report(report_data, cfg.CONF.report_template, cfg.CONF.report,
                    cfg.CONF.subunit)


if __name__ == "__main__":
    main()
