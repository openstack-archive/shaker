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
from shaker.engine import sla
from shaker.engine import utils
from shaker.engine import writer


LOG = logging.getLogger(__name__)


def calculate_stats(records, tests):
    # scenario -> test -> concurrency -> [record]
    rec_map = collections.defaultdict(
        functools.partial(collections.defaultdict,
                          functools.partial(collections.defaultdict, list)))

    for record in records.values():
        if 'test' not in record:
            continue

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
                    record_id = utils.make_record_id()
                    summary.update(dict(id=record_id,
                                        scenario=scenario, test=test,
                                        concurrency=concurrency,
                                        type='concurrency'))
                    records[record_id] = summary
                    concurrency_aggregates.append(summary)

            per_test_summary = aggregator.test_summary(concurrency_aggregates)
            if per_test_summary:
                record_id = utils.make_record_id()
                per_test_summary.update(dict(id=record_id,
                                             scenario=scenario, test=test,
                                             type='test'))
                records[record_id] = per_test_summary


def verify_sla(records, tests):
    record_map = collections.defaultdict(list)  # test -> [record]
    for r in records.values():
        if ('test' in r) and ('sla' in tests[r['test']]):
            record_map[r['test']].append(r)

    sla_records = []
    for test_id, records_per_test in record_map.items():
        for sla_expr in tests[test_id]['sla']:
            sla_records += sla.eval_expr(sla_expr, records_per_test)

    return sla_records


def log_sla(sla_records):
    if sla_records:
        LOG.info('*' * 80)
        for item in sla_records:
            test_id = _get_location(item.record) + ':' + item.expression
            LOG.info('%-73s %7s' % (test_id, '[%s]' % item.state))
        LOG.info('*' * 80)


def output_sla(sla_records):
    log_sla(sla_records)
    return [dict(record=item.record['id'], state=item.state,
                 expression=item.expression) for item in sla_records]


def _get_location(record):
    return '.'.join([str(record.get(s))
                     for s in ['scenario', 'test', 'concurrency',
                               'node', 'agent_id'] if record.get(s)])


def save_to_subunit(sla_records, subunit_filename):
    LOG.debug('Writing subunit stream to: %s', subunit_filename)
    fd = None
    state2subunit = {sla.STATE_TRUE: 'success',
                     sla.STATE_FALSE: 'fail'}
    try:
        fd = open(subunit_filename, 'w')
        output = subunit_v2.StreamResultToBytes(fd)

        for item in sla_records:
            output.startTestRun()
            test_id = _get_location(item.record) + ':' + item.expression

            if item.state != sla.STATE_TRUE:
                file_bytes = yaml.safe_dump(
                    item.record, default_flow_style=False).encode('utf8')
                output.status(test_id=test_id, file_name='results',
                              mime_type='text/plain; charset="utf8"', eof=True,
                              file_bytes=file_bytes)

            output.status(test_id=test_id,
                          test_status=state2subunit.get(item.state, 'skip'))
            output.stopTestRun()

        LOG.info('Subunit stream saved to: %s', subunit_filename)
    except IOError as e:
        LOG.error('Error writing subunit stream: %s', e)
    finally:
        if fd:
            fd.close()


def generate_report(data, report_template, report_filename, subunit_filename,
                    book_folder):

    calculate_stats(data['records'], data['tests'])

    sla_records = verify_sla(data['records'], data['tests'])
    data['sla'] = output_sla(sla_records)

    if subunit_filename:
        save_to_subunit(sla_records, subunit_filename)

    # add more filters to jinja
    jinja_env = jinja2.Environment(variable_start_string='[[[',
                                   variable_end_string=']]]',
                                   comment_start_string='[[#',
                                   comment_end_string='#]]')
    jinja_env.filters['json'] = json.dumps
    jinja_env.filters['yaml'] = functools.partial(yaml.safe_dump, indent=2,
                                                  default_flow_style=False)

    alias_mapper = lambda f: config.REPORT_TEMPLATES + '%s.html' % f
    template = utils.read_file(report_template, alias_mapper=alias_mapper)
    compiled_template = jinja_env.from_string(template)
    rendered_template = compiled_template.render(dict(report=data))

    if report_filename:
        LOG.debug('Writing report to: %s', report_filename)
        try:
            utils.write_file(rendered_template, report_filename)
            LOG.info('Report saved to: %s', report_filename)
        except IOError as e:
            LOG.error('Failed to write report file: %s', e)

    if book_folder:
        writer.write_book(book_folder, data)


def main():
    utils.init_config_and_logging(config.REPORT_OPTS + config.INPUT_OPTS)

    outputs = []
    for input_filename in cfg.CONF.input:
        LOG.debug('Reading JSON data from: %s', input_filename)
        outputs.append(json.loads(utils.read_file(input_filename)))

    aggregated = utils.merge_dicts(outputs)
    generate_report(aggregated, cfg.CONF.report_template, cfg.CONF.report,
                    cfg.CONF.subunit, cfg.CONF.book)


if __name__ == "__main__":
    main()
