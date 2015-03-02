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


class TestNetperfExecutor(testtools.TestCase):

    def test_get_command(self):
        executor = executors.NetperfExecutor({}, AGENT)

        expected = 'netperf -H %s -l 60 -t TCP_STREAM' % IP
        self.assertEqual(expected, executor.get_command())

    def test_get_command_options(self):
        executor = executors.NetperfExecutor(
            {'method': 'UDP_STREAM', 'time': 30}, AGENT)

        expected = 'netperf -H %s -l 30 -t UDP_STREAM' % IP
        self.assertEqual(expected, executor.get_command())
