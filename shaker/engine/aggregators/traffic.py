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

from oslo_log import log as logging

from shaker.engine.aggregators import base


LOG = logging.getLogger(__name__)


def _filter_none(array):
    return [x for x in array if x is not None]


def avg(array):
    s = _filter_none(array)
    return sum(s) / len(s) if s else 0


def safe_max(array):
    s = _filter_none(array)
    return max(s) if s else None


def safe_min(array):
    s = _filter_none(array)
    return min(s) if s else None


class TrafficAggregator(base.BaseAggregator):
    def __init__(self, test_definition):
        super(TrafficAggregator, self).__init__(test_definition)

    def test_summary(self, records):
        chart = []
        xs = []
        avg_v = collections.defaultdict(list)
        units = {}

        for record in sorted(records, key=lambda x: x['concurrency']):
            xs.append(record['concurrency'])
            for k, v in record['stats'].items():
                avg_v[k].append(v['avg'])
                units[k] = v['unit']

        chart.append(['concurrency'] + xs)
        meta = [('concurrency', '')]

        for k in avg_v.keys():
            chart.append([k] + avg_v[k])
            meta.append((k, units[k]))

        return {
            'chart': chart,
            'meta': meta,
        }

    def concurrency_summary(self, records):
        max_v = collections.defaultdict(list)
        min_v = collections.defaultdict(list)
        avg_v = collections.defaultdict(list)
        unit_v = dict()

        nodes = []
        for record in records:
            nodes.append(record['node'])

            for k, v in record['stats'].items():
                if 'max' in v:
                    max_v[k].append(v['max'])
                if 'min' in v:
                    min_v[k].append(v['min'])
                if 'avg' in v:
                    avg_v[k].append(v['avg'])
                if 'unit' in v:
                    unit_v[k] = v['unit']

        stats = {}
        node_chart = [['x'] + nodes]

        for k in unit_v.keys():
            stats[k] = dict()
            title = k
            if k in unit_v:
                stats[k]['unit'] = unit_v[k]
                title += ', ' + unit_v[k]
            if avg_v[k]:
                stats[k]['avg'] = avg(avg_v[k])
                node_chart.append(['Avg %s' % title] + avg_v[k])
            if max_v[k]:
                stats[k]['max'] = max(max_v[k])
                node_chart.append(['Max %s' % title] + max_v[k])
            if min_v[k]:
                stats[k]['min'] = min(min_v[k])
                node_chart.append(['Min %s' % title] + min_v[k])

        return {
            'stats': stats,
            'node_chart': node_chart,
        }

    def record_summary(self, record):
        # convert bit/s to Mbit/s
        for idx, item_meta in enumerate(record.get('meta', [])):
            if item_meta[1] in ['bit/s', 'bits/s']:
                for row in record.get('samples'):
                    if row[idx]:
                        row[idx] = float(row[idx]) / 1024 / 1024
                item_meta[1] = 'Mbit/s'

        # calculate stats
        record['stats'] = record.get('stats') or dict()

        for idx, item_meta in enumerate(record.get('meta', [])):
            column = [row[idx] for row in record.get('samples')]

            item_title = item_meta[0]
            if item_title != 'time':
                record['stats'][item_title] = {
                    'max': safe_max(column),
                    'min': safe_min(column),
                    'avg': avg(column),
                    'unit': item_meta[1],
                }

        # drop stdout
        if 'stdout' in record:
            del record['stdout']
