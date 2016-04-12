# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

import testtools

from shaker.engine.aggregators import traffic


class TestTrafficAggregator(testtools.TestCase):
    def test_agent_summary(self):
        aggregator = traffic.TrafficAggregator(None)

        original = {
            "stderr": "", "stdout": '',
            "meta": [["time", "s"], ["Ping ICMP", "ms"],
                     ["TCP download", "bit/s"]],
            "samples": [[0, 1.9, None],
                        [1, 2.4, None],
                        [2, 2.6, 60 * 1024 * 1024],
                        [3, 2.2, 65 * 1024 * 1024],
                        [4, 2.2, 61 * 1024 * 1024],
                        [5, 1.9, None]],
        }
        processed = copy.deepcopy(original)
        aggregator.record_summary(processed)

        self.assertFalse('stdout' in processed)

        expected_stats = {
            'Ping ICMP': {
                'max': 2.6,
                'min': 1.9,
                'avg': 2.2,
                'unit': 'ms',
            },
            'TCP download': {
                'max': 65.0,
                'min': 60.0,
                'avg': 62.0,
                'unit': 'Mbit/s',
            }
        }
        self.assertEqual(expected_stats, processed['stats'])

    def test_concurrency_summary(self):
        aggregator = traffic.TrafficAggregator(None)

        original = [
            {
                'agent_id': 'alpha_agent',
                'node': 'alpha',
                'stats': {
                    'Ping ICMP': {
                        'max': 2.6,
                        'min': 1.9,
                        'avg': 2.2,
                        'unit': 'ms',
                    },
                    'TCP download': {
                        'max': 65.0,
                        'min': 60.0,
                        'avg': 62.0,
                        'unit': 'Mbit/s',
                    }
                },
                'chart': [['time', 0, 1, 2, 3, 4, 5],
                          ['Ping ICMP', 1.9, 2.4, 2.6, 2.2, 2.2, 1.9],
                          ['TCP download', None, None, 60.0, 65.0, 61.0,
                          None]]
            },
            {
                'agent_id': 'beta_agent',
                'node': 'beta',
                'stats': {
                    'Ping ICMP': {
                        'max': 3.6,
                        'min': 2.9,
                        'avg': 3.2,
                        'unit': 'ms',
                    },
                    'TCP download': {
                        'max': 75.0,
                        'min': 70.0,
                        'avg': 72.0,
                        'unit': 'Mbit/s',
                    }
                },
                'chart': [['time', 0, 1, 2, 3, 4, 5],
                          ['Ping ICMP', 2.9, 3.4, 3.6, 3.2, 3.2, 2.9],
                          ['TCP download', None, None, 70.0, 75.0, 71.0,
                          None]]
            },
        ]

        aggregate = aggregator.concurrency_summary(original)
        expected_stats = {
            'Ping ICMP': {
                'max': 3.6,
                'min': 1.9,
                'avg': 2.7,
                'unit': 'ms',
            },
            'TCP download': {
                'max': 75.0,
                'min': 60.0,
                'avg': 67.0,
                'unit': 'Mbit/s',
            }
        }

        self.assertEqual(expected_stats, aggregate['stats'])
