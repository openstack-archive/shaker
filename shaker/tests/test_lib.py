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

import mock
import testtools

from shaker import lib


class TestLib(testtools.TestCase):

    @mock.patch('shaker.engine.quorum.make_quorum')
    def test_run_program(self, make_quorum_patch):
        quorum_mock = mock.MagicMock()
        make_quorum_patch.return_value = quorum_mock

        quorum_mock.execute = mock.Mock(
            return_value={'AGENT': {'status': 'ok', 'stdout': 'STDOUT', }})

        shaker = lib.Shaker('127.0.0.1:5999', ['AGENT'])
        res = shaker.run_program('AGENT', 'ls -al')

        self.assertDictContainsSubset(
            {'status': 'ok', 'stdout': 'STDOUT', 'agent': 'AGENT',
             'executor': 'shell', 'type': 'agent'}, res)
