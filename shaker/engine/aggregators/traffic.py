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
    return [x for x in array if x]


def mean(array):
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
        mean_v = collections.defaultdict(list)

        for record in records:
            xs.append(record['concurrency'])
            for k, v in record['stats'].items():
                mean_v[k].append(v['mean'])

        for k in mean_v.keys():
            chart.append(['Mean %s' % k] + mean_v[k])

        chart.append(['x'] + xs)
        return {
            'chart': chart,
        }

    def concurrency_summary(self, records):
        max_v = collections.defaultdict(list)
        min_v = collections.defaultdict(list)
        mean_v = collections.defaultdict(list)
        unit_v = dict()
        chart = []

        nodes = []
        for record in records:
            nodes.append(record['node'])
            chart += record['chart']

            for k, v in record['stats'].items():
                max_v[k].append(v['max'])
                min_v[k].append(v['min'])
                mean_v[k].append(v['mean'])
                unit_v[k] = v['unit']

        stats = {}
        node_chart = [['x'] + nodes]

        for k in max_v.keys():
            stats[k] = dict(max=max(max_v[k]),
                            min=min(min_v[k]),
                            mean=mean(mean_v[k]),
                            unit=unit_v[k])
            node_chart.append(['Mean %s' % k] + mean_v[k])
            node_chart.append(['Max %s' % k] + max_v[k])
            node_chart.append(['Min %s' % k] + min_v[k])

        return {
            'stats': stats,
            'x-chart': chart,
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
        record['stats'] = dict()
        record['chart'] = []

        for idx, item_meta in enumerate(record.get('meta', [])):
            column = [row[idx] for row in record.get('samples')]

            item_title = item_meta[0]
            if item_title != 'time':
                record['stats'][item_title] = {
                    'max': safe_max(column),
                    'min': safe_min(column),
                    'mean': mean(column),
                    'unit': item_meta[1],
                }
            record['chart'].append([item_title] + column)

        # drop stdout
        if 'stdout' in record:
            del record['stdout']
