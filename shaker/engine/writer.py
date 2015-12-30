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
import numbers
import os

import pygal
from pygal import style
import six
import yaml

from oslo_log import log as logging

LOG = logging.getLogger(__name__)

TABLE_FLOAT_PREC = 3


class ReSTPublisher(object):
    header_marks = ['*', '=', '-', '^', '~']

    def __init__(self, folder):
        self.folder = folder

        LOG.info('Create ReST book in: %s', folder)
        try:
            os.makedirs(folder)
        except OSError as e:
            LOG.warning(e)
        self.index = open(os.path.join(folder, 'index.rst'), 'w+')

    def __del__(self):
        self.index.close()

    def add_header(self, text, level=0):
        self.index.write(text)
        self.index.write('\n')
        self.index.write(self.header_marks[level] * len(text))
        self.index.write('\n\n')

    def add_subheader(self, text):
        self.index.write('**%s**:' % text)
        self.index.write('\n\n')

    def add_para(self, text):
        self.index.write(text)
        self.index.write('\n')

    def add_code(self, text):
        self.index.write('.. code-block:: yaml\n\n')
        for line in text.split('\n'):
            self.index.write(' ' * 4 + line + '\n')
        self.index.write('\n')

    def add_chart(self, chart_id, chart, meta):
        line_chart = pygal.Line(style=style.RedBlueStyle,
                                fill=True,
                                legend_at_bottom=True,
                                include_x_axis=True,
                                x_title='time')

        for i in range(1, len(meta)):
            kwargs = dict(secondary=True) if i == 2 else {}
            line_chart.add('%s, %s' % (meta[i][0], meta[i][1]), chart[i][1:],
                           **kwargs)

        line_chart.render_to_file(os.path.join(self.folder,
                                               '%s.svg' % chart_id))
        self.index.write('.. image:: %s.*\n\n' % chart_id)

    def add_chart_xy(self, chart_id, chart, meta):
        xy_chart = pygal.XY(style=style.RedBlueStyle,
                            legend_at_bottom=True,
                            fill=True,
                            include_x_axis=True,
                            x_title='concurrency',
                            )

        for i in range(1, len(meta)):
            v = [(chart[0][j], chart[i][j]) for j in range(1, len(chart[i]))]
            kwargs = dict(secondary=True) if i == 2 else {}
            xy_chart.add('%s, %s' % (meta[i][0], meta[i][1]), v, **kwargs)

        xy_chart.render_to_file(os.path.join(self.folder,
                                             '%s.svg' % chart_id))
        self.index.write('.. image:: %s.*\n\n' % chart_id)

    def add_table(self, table):
        widths = [max(len(c), TABLE_FLOAT_PREC) for c in table[0]]

        for r in table:
            for i in range(len(widths)):
                if isinstance(r[i], six.string_types):
                    widths[i] = max(widths[i], len(r[i]))

        # header
        for w in widths:
            self.index.write('=' * w)
            self.index.write('  ')

        self.index.write('\n')

        for i in range(len(widths)):
            c = table[0][i]
            self.index.write('{0:<{1}}'.format(c, widths[i]))
            self.index.write('  ')

        self.index.write('\n')

        for w in widths:
            self.index.write('=' * w)
            self.index.write('  ')

        self.index.write('\n')

        for r in table[1:]:
            for i in range(len(widths)):
                c = r[i]
                if isinstance(c, numbers.Integral):
                    c = '{0:>{1}}'.format(c, widths[i])
                elif isinstance(c, numbers.Number):
                    c = '{0:>{1}.{2}f}'.format(c, widths[i], TABLE_FLOAT_PREC)
                else:
                    c = '{0:<{1}}'.format(c, widths[i])
                self.index.write(c)
                self.index.write('  ')

            self.index.write('\n')

        for w in widths:
            self.index.write('=' * w)
            self.index.write('  ')

        self.index.write('\n\n')


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
    publisher.add_subheader('Scenario')
    publisher.add_code(yamlize(scenario))


def write_test_definition(data, publisher, test):
    publisher.add_subheader('Test Specification')
    publisher.add_code(yamlize(data['tests'][test]))


def _get_location(record):
    return '.'.join([str(record.get(s))
                     for s in ['test', 'concurrency', 'node', 'agent_id']
                     if record.get(s)])


def write_sla(publisher, sla_records, records):
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
        publisher.add_subheader('SLA')
        publisher.add_table(table)


def write_concurrency_block(publisher, all_records, local_records):
    for record in local_records:
        concurrency = record['concurrency']
        if len(local_records) > 2:
            publisher.add_header('Concurrency %s' % concurrency, level=2)

        agent_records = filter_records(all_records,
                                       type='agent',
                                       scenario=record['scenario'],
                                       test=record['test'],
                                       concurrency=concurrency,
                                       status='ok')

        if len(agent_records) <= 2 and len(local_records) <= 2:
            # go into details
            write_agent_block_detailed(publisher, agent_records)
        else:
            # show stats only
            show_stats(publisher, agent_records, 'node')


def write_agent_block_detailed(publisher, records):
    for record in records:
        if len(records) > 1:
            publisher.add_header('Agent %s' % record['agent'], level=3)

        if record.get('chart'):
            publisher.add_chart(record['id'], record['chart'], record['meta'])

        publisher.add_subheader('Stats')
        publisher.add_code(yamlize(record['stats']))


def show_stats(publisher, records, row_header):
    if len(records) < 1:
        return

    publisher.add_subheader('Stats')
    records.sort(key=lambda x: x[row_header])

    keys = ['min', 'mean', 'max']
    meta = []
    headers = []

    # collect meta
    record = records[0]
    headers.append(row_header)

    for param, values in record['stats'].items():
        for key in keys:
            if values['unit']:
                headers.append('%s %s, %s' % (key, param, values['unit']))
            else:
                headers.append('%s %s' % (key, param))
            meta.append((param, key))

    # fill the table
    table = [headers]
    for record in records:
        row = [record[row_header]]
        for m in meta:
            param, key = m
            row.append(record['stats'][param][key])
        table.append(row)

    publisher.add_table(table)


def write_book(doc_folder, data):
    records = data['records'].values()
    publisher = ReSTPublisher(doc_folder)

    for scenario in data['scenarios'].keys():
        publisher.add_header(scenario)
        write_scenario_definition(publisher, data['scenarios'][scenario])

        test_records = filter_records(records, type='test', scenario=scenario)
        test_records.sort(key=lambda x: x['test'])

        for record in test_records:
            test = record['test']
            publisher.add_header(test, level=1)

            write_test_definition(data, publisher, test)

            concurrency_records = filter_records(records, type='concurrency',
                                                 scenario=scenario, test=test)
            concurrency_records.sort(key=lambda x: int(x['concurrency']))

            concurrency_count = len(concurrency_records)

            if concurrency_count > 0:
                if record.get('chart'):
                    publisher.add_chart_xy(record['id'], record['chart'],
                                           record['meta'])
                    show_stats(publisher, concurrency_records, 'concurrency')

            write_sla(publisher, data['sla'],
                      filter_records(records, scenario=scenario, test=test))

            write_concurrency_block(publisher, records, concurrency_records)
