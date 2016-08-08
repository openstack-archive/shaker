# Copyright (c) 2016 Mirantis Inc.
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
import numbers
import os
import textwrap

from oslo_log import log as logging
import pygal
from pygal import style
import six
import yaml

from shaker.engine import utils

LOG = logging.getLogger(__name__)

TABLE_FLOAT_PREC = 2


class ReSTPublisher(object):
    header_marks = ['*', '=', '-', '^', '~']

    def __init__(self, folder):
        self.folder = folder

        LOG.info('Create ReST book in: %s', folder)
        utils.mkdir_tree(folder)
        self.index = open(os.path.join(folder, 'index.rst'), 'w+')

    def __del__(self):
        self.index.close()

    def ref_label(self, text):
        self.index.write('.. _%s:\n\n' % utils.strict(text))

    def header(self, text, level=0):
        self.index.write(text)
        self.index.write('\n')
        self.index.write(self.header_marks[level] * len(text))
        self.index.write('\n\n')

    def subheader(self, text):
        self.index.write('**%s**:' % text)
        self.index.write('\n\n')

    def para(self, text):
        self.index.write(textwrap.fill(text, width=79))
        self.index.write('\n\n')

    def code(self, text):
        self.index.write('.. code-block:: yaml\n\n')
        for line in text.split('\n'):
            if line:
                self.index.write(' ' * 4 + line + '\n')
        self.index.write('\n')

    def chart_line(self, chart_id, samples, meta, x_title):
        line_chart = pygal.Line(style=style.RedBlueStyle,
                                fill=False,
                                legend_at_bottom=True,
                                include_x_axis=True,
                                x_title=x_title)

        for i in range(1, len(meta)):
            line_title = meta[i][0]
            if meta[i][1]:
                line_title += ', %s' % meta[i][1]
            kwargs = dict(secondary=True) if i == 2 else {}
            values = [samples[x][i] for x in range(len(samples))]
            line_chart.add(line_title, values, **kwargs)

        line_chart.render_to_file(os.path.join(self.folder,
                                               '%s.svg' % chart_id))
        self.index.write('.. image:: %s.*\n\n' % chart_id)

    def chart_xy(self, chart_id, chart, meta, x_title):
        xy_chart = pygal.XY(style=style.RedBlueStyle,
                            legend_at_bottom=True,
                            fill=False,
                            include_x_axis=True,
                            x_title=x_title)

        for i in range(1, len(meta)):
            line_title = meta[i][0]
            if meta[i][1]:
                line_title += ', %s' % meta[i][1]
            v = [(chart[0][j], chart[i][j]) for j in range(1, len(chart[i]))]
            kwargs = dict(secondary=True) if i == 2 else {}
            xy_chart.add(line_title, v, **kwargs)

        xy_chart.render_to_file(os.path.join(self.folder,
                                             '%s.svg' % chart_id))
        self.index.write('.. image:: %s.*\n\n' % chart_id)

    def _outline(self, widths):
        s = '  '.join('=' * w for w in widths)
        self.index.write(s)
        self.index.write('\n')

    def table(self, t):
        widths = [max(len(c), TABLE_FLOAT_PREC + 6) for c in t[0]]

        for r in t:
            for i in range(len(widths)):
                if isinstance(r[i], six.string_types):
                    widths[i] = max(widths[i], len(r[i]))

        # header
        self._outline(widths)
        self.index.write('  '.join(('{0:<{1}}'.format(t[0][i], widths[i]))
                                   for i in range(len(widths))))
        self.index.write('\n')
        self._outline(widths)

        # body
        for r in t[1:]:
            cells = []
            for i in range(len(widths)):
                c = r[i]
                if isinstance(c, numbers.Integral):
                    c = '{0:>{1}}'.format(c, widths[i])
                elif isinstance(c, numbers.Number):
                    c = '{0:>{1}.{2}f}'.format(c, widths[i], TABLE_FLOAT_PREC)
                else:
                    c = '{0:<{1}}'.format(c, widths[i])
                cells.append(c)

            self.index.write('  '.join(cells).rstrip())
            self.index.write('\n')

        # bottom border
        self._outline(widths)
        self.index.write('\n')


yamlize = functools.partial(yaml.safe_dump, indent=2, default_flow_style=False)


def filter_records(records, **kwargs):
    result = []
    for r in records:
        f = True
        for param, value in kwargs.items():
            f &= r.get(param) == value

        if f:
            result.append(r)
    return result


def write_scenario_definition(publisher, scenario):
    publisher.subheader('Scenario')
    publisher.code(yamlize(scenario))


def write_test_definition(data, publisher, test):
    publisher.subheader('Test Specification')
    publisher.code(yamlize(data['tests'][test]))


def write_sla(publisher, records, sla_records):
    table = [['Expression', 'Concurrency', 'Node', 'Result']]

    for sla_record in sla_records:
        expression = sla_record['expression']
        record_id = sla_record['record']
        state = sla_record['state']

        for record in records:
            if record['id'] == record_id:
                table.append([expression, record['concurrency'],
                              record['node'], state])
                break

    if len(table) > 1:
        publisher.subheader('SLA')
        publisher.table(table)


def write_record_stats(publisher, record):
    table = [['Metric', 'Min', 'Avg', 'Max']]
    stats = record['stats']

    for key in stats.keys():
        metric = key
        unit = stats[key].get('unit') or ''
        if unit:
            metric += ', %s' % unit

        s = stats[key]
        value_min = s.get('min') or ''
        value_avg = s.get('avg') or ''
        value_max = s.get('max') or ''

        table.append([metric, value_min, value_avg, value_max])

    if len(table) > 1:
        publisher.subheader('Stats')
        publisher.table(table)


def write_errors(publisher, records):
    bad_records = [r for r in records if r.get('status') in {'lost', 'error'}]
    if bad_records:
        publisher.subheader('Errors')
        for rec in bad_records:
            publisher.code(yamlize(rec))


def write_concurrency_block(publisher, all_records, local_records, sla):
    for record in local_records:
        concurrency = record['concurrency']
        if len(local_records) > 2:
            publisher.header('Concurrency %s' % concurrency, level=2)

        agent_records = filter_records(all_records,
                                       type='agent',
                                       scenario=record['scenario'],
                                       test=record['test'],
                                       concurrency=concurrency)

        agent_records_ok = filter_records(agent_records, status='ok')

        write_errors(publisher, agent_records)

        if len(agent_records_ok) <= 2 and len(local_records) <= 2:
            # go into details
            write_agent_block_detailed(publisher, agent_records_ok)
        else:
            # show stats only
            write_stats(publisher, agent_records_ok, 'node')

        write_sla(publisher, agent_records_ok, sla)


def write_agent_block_detailed(publisher, records):
    for record in records:
        if len(records) > 1:
            publisher.header('Agent %s' % record['agent'], level=3)

        if record.get('samples'):
            publisher.chart_line(record['id'], record['samples'],
                                 record['meta'], x_title='time, s')

        write_record_stats(publisher, record)


def write_stats(publisher, records, row_header, show_all=False):
    if len(records) < 1:
        return

    publisher.subheader('Stats')
    records.sort(key=lambda x: x[row_header])

    if show_all:
        keys = ['min', 'avg', 'max']
    else:
        keys = ['avg']
    meta = []
    headers = []

    # collect meta
    record = records[0]
    headers.append(row_header)

    for param, values in record['stats'].items():
        for key in keys:
            header = ''
            if show_all:
                header = key + ' '
            header += param
            if values['unit']:
                header += ', ' + values['unit']
            headers.append(header)
            meta.append((param, key))

    # fill the table
    table = [headers]
    for record in records:
        row = [record[row_header]]
        for m in meta:
            param, key = m

            if param in record['stats']:
                row.append(record['stats'][param][key])
            else:
                row.append('n/a')

        table.append(row)

    publisher.table(table)


def write_book(doc_folder, data):
    records = data['records'].values()
    publisher = ReSTPublisher(doc_folder)

    for scenario in data['scenarios'].keys():
        publisher.ref_label(scenario)
        publisher.header(scenario)

        scenario_def = data['scenarios'][scenario]
        if 'description' in scenario_def:
            publisher.para(scenario_def['description'])

        write_scenario_definition(publisher, scenario_def)

        write_errors(publisher, filter_records(records, scenario=scenario))

        test_records = filter_records(records, type='test', scenario=scenario)
        test_records.sort(key=lambda x: x['test'])

        for record in test_records:
            test = record['test']
            publisher.header(test, level=1)

            write_test_definition(data, publisher, test)

            concurrency_records = filter_records(records, type='concurrency',
                                                 scenario=scenario, test=test)
            concurrency_records.sort(key=lambda x: int(x['concurrency']))

            concurrency_count = len(concurrency_records)

            if concurrency_count >= 2:
                if record.get('chart'):
                    publisher.chart_xy(record['id'], record['chart'],
                                       record['meta'], 'concurrency')
                    write_stats(publisher, concurrency_records, 'concurrency')

            write_sla(publisher, concurrency_records, data['sla'])

            write_concurrency_block(publisher, records, concurrency_records,
                                    data['sla'])
