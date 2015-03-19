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

from shaker.engine.executors import netperf


IP = '10.0.0.10'
AGENT = {'slave': {'ip': IP}}


class TestNetperfWrapperExecutor(testtools.TestCase):

    def test_get_command(self):
        executor = netperf.NetperfWrapperExecutor({}, AGENT)

        expected = {'data': ('netperf-wrapper -H %s -l 60 -s 1 '
                             '-f csv tcp_download') % IP,
                    'type': 'program'}
        self.assertEqual(expected, executor.get_command())

    def test_get_command_with_params(self):
        executor = netperf.NetperfWrapperExecutor(
            dict(method='ping', time=10, interval=0.5), AGENT)

        expected = {'data': ('netperf-wrapper -H %s -l 10 -s 0.5 '
                             '-f csv ping') % IP,
                    'type': 'program'}
        self.assertEqual(expected, executor.get_command())

    def test_process_reply(self):
        executor = netperf.NetperfWrapperExecutor({}, AGENT)
        message = {
            'stdout': """tcp_download,Ping ICMP,TCP download
0.0,0.09,
2.0,0.0800211283506,
4.0,0.0602545096056,
6.0,0.0502416561724,28555.9
8.0,0.05,25341.9871721
10.0,0.0500947171761,30486.4518264
12.0,0.0603484557656,
14.0,0.0603987445198,
"""
        }
        expected = {
            'samples': [
                [0.0, 0.09, None],
                [2.0, 0.0800211283506, None],
                [4.0, 0.0602545096056, None],
                [6.0, 0.0502416561724, 28555.9],
                [8.0, 0.05, 25341.9871721],
                [10.0, 0.0500947171761, 30486.4518264],
                [12.0, 0.0603484557656, None],
                [14.0, 0.0603987445198, None],
            ],
            'meta': [
                ['time', 's'], ['Ping ICMP', 'ms'], ['TCP download', 'Mbps'],
            ]
        }
        reply = executor.process_reply(message)
        self.assertEqual(expected['samples'], reply['samples'],
                         message='Samples data')
        self.assertEqual(expected['meta'], reply['meta'],
                         message='Metadata')
