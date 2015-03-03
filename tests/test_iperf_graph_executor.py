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

from shaker.engine import executors


IP = '10.0.0.10'
AGENT = {'slave': {'ip': IP}}


class TestIperfGraphExecutor(testtools.TestCase):

    def test_get_command(self):
        executor = executors.IperfGraphExecutor({}, AGENT)

        expected = ('sudo nice -n -20 iperf --client %s --format m --nodelay '
                    '--len 8k --time 60 --parallel 1 '
                    '--reportstyle C --interval 1') % IP
        self.assertEqual(expected, executor.get_command())

    def test_get_command_udp(self):
        executor = executors.IperfGraphExecutor(
            {'udp': True, 'time': 30}, AGENT)

        expected = ('sudo nice -n -20 iperf --client %s --format m --nodelay '
                    '--len 8k --udp --time 30 --parallel 1 '
                    '--reportstyle C --interval 1') % IP
        self.assertEqual(expected, executor.get_command())

    def test_process_reply(self):
        executor = executors.IperfGraphExecutor({}, AGENT)
        message = {
            'stdout': """
20150224134955,172.1.7.77,47351,172.1.76.77,5001,3,0.0-1.0,50068684,399507456
20150224134956,172.1.7.77,47351,172.1.76.77,5001,3,1.0-2.0,51605504,412090368
20150224134957,172.1.7.77,47351,172.1.76.77,5001,3,2.0-3.0,50843648,405798912
20150224134957,172.1.7.77,47351,172.1.76.77,5001,3,0.0-3.0,150843648,400000002
"""
        }
        expected = {
            'samples': [
                executors.Sample(0.0, 1.0, 399507456),
                executors.Sample(1.0, 2.0, 412090368),
                executors.Sample(2.0, 3.0, 405798912),
            ],
            'row_data': [
                [1.0, 399507456],
                [2.0, 412090368],
                [3.0, 405798912],
            ],
            'stats': {
                'duration': 3.0,
                'max': 412090368,
                'min': 399507456,
                'mean': (399507456 + 412090368 + 405798912) / 3,
                'total': (399507456 + 412090368 + 405798912),
            },
        }
        reply = executor.process_reply(message)
        self.assertEqual(expected['samples'], reply['samples'],
                         message='Samples data')
        self.assertEqual(expected['row_data'], reply['row_data'],
                         'Row data')
        self.assertEqual(expected['stats'], reply['stats'],
                         'Traffic stats')
