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

from shaker.engine import server


class TestServer(testtools.TestCase):

    def test_extend_agents(self):
        agents_map = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'mode': 'master',
                'node': 'uno',
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'node': 'dos'},
        }
        agents = server._extend_agents(agents_map)
        self.assertDictContainsSubset(agents['UU1D_master_0']['slave'],
                                      agents['UU1D_slave_0'])
        self.assertDictContainsSubset(agents['UU1D_slave_0']['master'],
                                      agents['UU1D_master_0'])

    def test_pick_agents_full(self):
        agents = {}
        for i in range(10):
            agents[i] = {
                'id': i, 'mode': 'alone', 'node': 'uno',
            }
        picked = [set(a['id'] for a in arr)
                  for arr in server._pick_agents(agents, 'full')]
        self.assertEqual([set(range(10))], picked)

    def test_pick_agents_full_filter_slaves(self):
        agents = {}
        for i in range(10):
            agents['master_%s' % i] = {
                'id': 'master_%s' % i, 'mode': 'master', 'node': 'uno',
            }
            agents['slave_%s' % i] = {
                'id': 'slave_%s' % i, 'mode': 'slave', 'node': 'uno',
            }
        picked = [set(a['id'] for a in arr)
                  for arr in server._pick_agents(agents, 'full')]
        self.assertEqual([set('master_%s' % i for i in range(10))],
                         picked)

    def test_pick_agents_linear(self):
        agents = {}
        for i in range(10):
            agents[i] = {
                'id': i, 'mode': 'alone', 'node': 'uno',
            }
        picked = [set(a['id'] for a in arr)
                  for arr in server._pick_agents(agents, 'linear_progression')]
        self.assertEqual([set(range(i + 1)) for i in range(0, 10)],
                         picked)

    def test_pick_agents_quadratic(self):
        agents = {}
        for i in range(10):
            agents[i] = {
                'id': i, 'mode': 'alone', 'node': 'uno',
            }
        picked = [set(a['id'] for a in arr)
                  for arr in server._pick_agents(agents,
                                                 'quadratic_progression')]
        self.assertEqual([set(range(1)), set(range(2)),
                          set(range(5)), set(range(10))],
                         picked)
