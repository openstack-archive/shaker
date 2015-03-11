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

import uuid

from oslo_log import log as logging

from shaker.engine.aggregators import base


LOG = logging.getLogger(__name__)


def mean(array):
    if not array:
        return 0
    return sum(array) / len(array)


class TrafficAggregator(base.BaseAggregator):
    def __init__(self, test_definition):
        super(TrafficAggregator, self).__init__(test_definition)

    def iteration_summary(self, iteration_data):
        max_v = []
        min_v = []
        mean_v = []
        nodes = []
        for one in iteration_data['results_per_agent']:
            nodes.append(one['agent']['node'])
            max_v.append(one['stats']['max'])
            min_v.append(one['stats']['min'])
            mean_v.append(one['stats']['mean'])

        iteration_data.update({
            'stats': {
                'max': max(max_v),
                'min': min(min_v),
                'mean': mean(mean_v),
            },
            'agent_chart': {
                'uuid': uuid.uuid4(),
                'data': [
                    ['x'] + nodes,
                    ['min'] + min_v,
                    ['mean'] + mean_v,
                    ['max'] + max_v,
                ]
            }
        })

    def agent_summary(self, agent_data):
        # convert bps to Mbps
        for idx, item_meta in enumerate(agent_data['meta']):
            if item_meta[1] == 'bps':
                for row in agent_data['samples']:
                    row[idx] = float(row[idx]) / 1024 / 1024
                item_meta[1] = 'Mbps'

        # calculate stats
        agent_data['stats'] = dict()
        agent_data['chart'] = []

        for idx, item_meta in enumerate(agent_data['meta']):
            column = [row[idx] for row in agent_data['samples']]

            if item_meta[1] == 'Mbps':
                agent_data['stats']['max'] = max(column)
                agent_data['stats']['min'] = min(column)
                agent_data['stats']['mean'] = mean(column)

            agent_data['chart'].append([item_meta[0]] + column)

        # drop stdout
        del agent_data['stdout']
