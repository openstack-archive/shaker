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


def calculate_stats(records, tests):
    aggregates = []
    # scenario -> test -> concurrency -> [record]
    rec_map = collections.defaultdict(
        functools.partial(collections.defaultdict,
                          functools.partial(collections.defaultdict, list)))

    for record in records:
        aggregator = aggregators.get_aggregator(tests[record['test']])
        aggregator.record_summary(record)

        rec_map[record['scenario']][record['test']][
            record['concurrency']].append(record)

    for scenario, per_scenario in rec_map.items():
        for test, per_test in per_scenario.items():
            aggregator = aggregators.get_aggregator(tests[test])

            concurrency_aggregates = []
            for concurrency, per_concurrency in per_test.items():
                summary = aggregator.concurrency_summary(per_concurrency)
                if summary:
                    summary.update(dict(scenario=scenario, test=test,
                                        concurrency=concurrency,
                                        type='agg_concurrency'))
                    aggregates.append(summary)
                    concurrency_aggregates.append(summary)

            per_test_summary = aggregator.test_summary(concurrency_aggregates)
            if per_test_summary:
                per_test_summary.update(dict(scenario=scenario, test=test,
                                             type='agg_test'))
                aggregates.append(per_test_summary)

    return aggregates

SLARecord = collections.namedtuple('SLARecord',
                                   ['sla', 'status', 'location', 'stats'])


def _verify_stats_against_sla(sla, record, location):
    res = []
    for term in sla:
        status = utils.eval_expr(term, record['stats'])
        sla_record = SLARecord(sla=term, status=status,
                               location=location, stats=record['stats'])
        res.append(sla_record)
        LOG.debug('SLA: %s', sla_record)
    return res


def verify_sla(records, tests):
    sla_results = []
    # test -> [sla]
    sla_map = dict((test_id, test['sla'])
                   for test_id, test in tests.items() if 'sla' in test)

    for record in records:
        if (record['test'] in sla_map) and ('stats' in record):
            sla = sla_map[record['test']]
            path = [str(record[key])
                    for key in ['test', 'concurrency', 'node', 'agent_id']
                    if key in record]
            info = _verify_stats_against_sla(sla, record, '.'.join(path))
            sla_results += info
            record['sla_info'] = info
    return sla_results


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

    data['records'] += calculate_stats(data['records'], data['tests'])

    sla_res = verify_sla(data['records'], data['tests'])

    if subunit_filename:
        save_to_subunit(sla_res, subunit_filename)

    # add more filters to jinja
    jinja_env = jinja2.Environment(variable_start_string='[[[',
                                   variable_end_string=']]]',
                                   comment_start_string='[[#',
                                   comment_end_string='#]]')
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
