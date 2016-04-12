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

import testtools

from shaker.engine import report
from shaker.engine import sla


class TestReport(testtools.TestCase):

    def test_verify_sla(self):
        records = {0: {'id': 0, 'type': 'agent', 'test': 'iperf_tcp',
                       'stats': {'bandwidth': {'avg': 700, 'min': 400}}},
                   1: {'id': 1, 'type': 'agent', 'test': 'iperf_udp',
                       'stats': {'bandwidth': {'avg': 1000, 'min': 800}}},
                   2: {'id': 2, 'type': 'agent', 'test': 'iperf_tcp',
                       'stats': {'bandwidth': {'avg': 850, 'min': 600}}}}

        tests = {
            'iperf_tcp': {
                'sla': [
                    '[type == "agent"] >> (stats.bandwidth.avg > 800)',
                    '[type == "agent"] >> (stats.bandwidth.min > 500)',
                ],
            },
            'iperf_udp': {
                'sla': [
                    '[type == "agent"] >> (stats.bandwidth.avg > 900)',
                ],
            }
        }

        sla_records = report.verify_sla(records, tests)

        self.assertIn(sla.SLAItem(records[0], sla.STATE_FALSE,
                                  'stats.bandwidth.avg > 800'), sla_records)
        self.assertIn(sla.SLAItem(records[0], sla.STATE_FALSE,
                                  'stats.bandwidth.min > 500'), sla_records)

        self.assertIn(sla.SLAItem(records[1], sla.STATE_TRUE,
                                  'stats.bandwidth.avg > 900'), sla_records)

        self.assertIn(sla.SLAItem(records[2], sla.STATE_TRUE,
                                  'stats.bandwidth.avg > 800'), sla_records)
        self.assertIn(sla.SLAItem(records[2], sla.STATE_TRUE,
                                  'stats.bandwidth.min > 500'), sla_records)
