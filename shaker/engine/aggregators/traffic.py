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
import uuid

from oslo_log import log as logging

from shaker.engine.aggregators import base


LOG = logging.getLogger(__name__)


def mean(array):
    if not array:
        return 0
    array = [x for x in array if x]
    return sum(array) / len(array)


def safe_max(array):
    return max(x for x in array if x)


def safe_min(array):
    return min(x for x in array if x)


class TrafficAggregator(base.BaseAggregator):
    def __init__(self, test_definition):
        super(TrafficAggregator, self).__init__(test_definition)

    def test_summary(self, test_data):
        chart = []
        xs = []
        mean_v = collections.defaultdict(list)

        for iteration in test_data['results_per_iteration']:
            xs.append(len(iteration['results_per_agent']))
            for k, v in iteration['stats'].items():
                mean_v[k].append(v['mean'])

        for k in mean_v.keys():
            chart.append(['Mean %s' % k] + mean_v[k])

        chart.append(['x'] + xs)
        test_data.update({
            'chart': chart,
        })

    def iteration_summary(self, iteration_data):
        max_v = collections.defaultdict(list)
        min_v = collections.defaultdict(list)
        mean_v = collections.defaultdict(list)
        unit_v = dict()
        chart = []

        nodes = []
        for one in iteration_data['results_per_agent']:
            nodes.append(one['agent']['node'])
            chart += one['chart']

            for k, v in one['stats'].items():
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

        iteration_data.update({
            'uuid': uuid.uuid4(),
            'stats': stats,
            'x-chart': chart,
            'node_chart': node_chart,
        })

    def agent_summary(self, agent_data):
        # convert bps to Mbps
        for idx, item_meta in enumerate(agent_data['meta']):
            if item_meta[1] == 'bps':
                for row in agent_data['samples']:
                    if row[idx]:
                        row[idx] = float(row[idx]) / 1024 / 1024
                item_meta[1] = 'Mbps'

        # calculate stats
        agent_data['stats'] = dict()
        agent_data['chart'] = []

        for idx, item_meta in enumerate(agent_data['meta']):
            column = [row[idx] for row in agent_data['samples']]

            item_title = item_meta[0]
            if item_title != 'time':
                agent_data['stats'][item_title] = {
                    'max': safe_max(column),
                    'min': safe_min(column),
                    'mean': mean(column),
                    'unit': item_meta[1],
                }
            agent_data['chart'].append([item_title] + column)

        # drop stdout
        del agent_data['stdout']
