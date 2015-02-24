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

        expected = ('sudo nice -n -20 iperf --client %s --format m '
                    '--len 8k --nodelay --time 60 --parallel 1 '
                    '-y C --interval 1') % IP
        self.assertEqual(expected, executor.get_command())

    def test_process_reply(self):
        executor = executors.IperfGraphExecutor({}, AGENT)
        message = {
            'stdout': """
20150224134955,172.18.76.77,47351,172.18.76.77,5001,3,0.0-1.0,500686848,4005494784
20150224134956,172.18.76.77,47351,172.18.76.77,5001,3,1.0-2.0,516055040,4128440320
20150224134957,172.18.76.77,47351,172.18.76.77,5001,3,2.0-3.0,508436480,4067491840
"""
        }
        expected = {
            'samples': {
                '3': [
                    dict(time=1.0, transfer=500686848, bandwidth=4005494784),
                    dict(time=2.0, transfer=516055040, bandwidth=4128440320),
                    dict(time=3.0, transfer=508436480, bandwidth=4067491840),
                ]
            },
            'bandwidth_max': {'3': 4128440320},
            'bandwidth_min': {'3': 4005494784},
            'bandwidth_avg': {'3': (4005494784 + 4128440320 + 4067491840) / 3},
        }
        reply = executor.process_reply(message)
        self.assertEqual(expected['samples'], reply['samples'])
        self.assertEqual(expected['bandwidth_max'], reply['bandwidth_max'])
        self.assertEqual(expected['bandwidth_min'], reply['bandwidth_min'])
        self.assertEqual(expected['bandwidth_avg'], reply['bandwidth_avg'])
