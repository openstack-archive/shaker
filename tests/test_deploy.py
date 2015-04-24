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

from shaker.engine import deploy


class TestDeploy(testtools.TestCase):

    def test_generate_agents_alone_single_room(self):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'node': 'dos'},
        }
        actual = deploy.generate_agents(['uno', 'dos'],
                                        ['single_room'],
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_single_room(self):
        unique = 'UU1D'
        expected = {
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
        actual = deploy.generate_agents(['uno', 'dos', 'tre'],
                                        ['pair', 'single_room'],
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_single_room_not_enough(self):
        unique = 'UU1D'
        self.assertRaises(Exception, deploy.generate_agents, ['uno'],
                          ['pair', 'single_room'], unique)  # NOQA

    def test_generate_agents_pair_double_room(self):
        unique = 'UU1D'
        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'mode': 'master',
                'node': 'uno',
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'node': 'uno'},
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'mode': 'master',
                'node': 'dos',
                'slave_id': 'UU1D_slave_1'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'mode': 'slave',
                'node': 'dos'},
            'UU1D_master_2': {
                'id': 'UU1D_master_2',
                'mode': 'master',
                'node': 'tre',
                'slave_id': 'UU1D_slave_2'},
            'UU1D_slave_2': {
                'id': 'UU1D_slave_2',
                'master_id': 'UU1D_master_2',
                'mode': 'slave',
                'node': 'tre'},
        }
        actual = deploy.generate_agents(['uno', 'dos', 'tre'],
                                        ['pair', 'double_room'],
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_mixed_room(self):
        unique = 'UU1D'
        expected = {
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
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'mode': 'master',
                'node': 'dos',
                'slave_id': 'UU1D_slave_1'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'mode': 'slave',
                'node': 'uno'},
        }
        actual = deploy.generate_agents(['uno', 'dos'],
                                        ['pair', 'mixed_room'],
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_alone_single_room_double_density(self):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'node': 'uno'},
        }
        actual = deploy.generate_agents(['uno'],
                                        ['single_room', {'density': 2}],
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_alone_single_room_compute_nodes(self):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'node': 'duo'},
        }
        actual = deploy.generate_agents(['uno', 'duo', 'tre'],
                                        ['single_room', {'compute_nodes': 2}],
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_alone_single_room_density_compute_nodes(self):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'node': 'uno'},
        }
        actual = deploy.generate_agents(['uno', 'duo', 'tre'],
                                        ['single_room', {'compute_nodes': 1},
                                         {'density': 2}],
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_single_room_density_compute_nodes(self):
        unique = 'UU1D'
        actual = deploy.generate_agents(['uno', 'duo', 'tre'],
                                        ['pair', 'single_room',
                                         {'density': 4}, {'compute_nodes': 2}],
                                        unique)
        self.assertEqual(8, len(actual))

    def test_filter_agents_all_deployed(self):
        agents = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'node': 'dos'},
        }
        stack_outputs = {
            'UU1D_agent_0_ip': '10.0.0.1',
            'UU1D_agent_0_instance_name': 'i-000001',
            'UU1D_agent_1_ip': '10.0.0.2',
            'UU1D_agent_1_instance_name': 'i-000002',
        }
        filtered = deploy.filter_agents(agents, stack_outputs)
        self.assertEqual(agents, filtered)

    def test_filter_agents_partial_deployed(self):
        agents = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'node': 'dos'},
        }
        stack_outputs = {
            'UU1D_agent_0_ip': '10.0.0.1',
            'UU1D_agent_0_instance_name': 'i-000001',
        }
        expected = {'UU1D_agent_0': agents['UU1D_agent_0']}
        filtered = deploy.filter_agents(agents, stack_outputs)
        self.assertEqual(expected, filtered)

    def test_filter_agents_pair_single_room(self):
        agents = {
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
        stack_outputs = {
            'UU1D_master_0_ip': '10.0.0.1',
            'UU1D_master_0_instance_name': 'i-000001',
            'UU1D_slave_0_ip': '10.0.0.2',
            'UU1D_slave_0_instance_name': 'i-000002',
        }
        expected = {'UU1D_master_0': agents['UU1D_master_0'],
                    'UU1D_slave_0': agents['UU1D_slave_0']}

        filtered = deploy.filter_agents(agents, stack_outputs)
        self.assertEqual(expected, filtered)

    def test_filter_agents_pair_double_room_partially_deployed(self):
        agents = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'mode': 'master',
                'node': 'uno',
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'node': 'uno'},
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'mode': 'master',
                'node': 'dos',
                'slave_id': 'UU1D_slave_1'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'mode': 'slave',
                'node': 'dos'},
        }
        stack_outputs = {
            'UU1D_master_0_ip': '10.0.0.1',
            'UU1D_master_0_instance_name': 'i-000001',
            'UU1D_slave_0_ip': '10.0.0.2',
            'UU1D_slave_0_instance_name': 'i-000002',
            'UU1D_master_1_ip': '10.0.0.3',
            'UU1D_master_1_instance_name': 'i-000003',
            'UU1D_slave_1_instance_name': 'i-000004',
        }
        expected = {'UU1D_master_0': agents['UU1D_master_0'],
                    'UU1D_slave_0': agents['UU1D_slave_0'], }

        filtered = deploy.filter_agents(agents, stack_outputs)
        self.assertEqual(expected, filtered)
