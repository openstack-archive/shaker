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

from shaker.engine import deploy


ZONE = 'zone'


def nodes_helper(*nodes):
    return [dict(host=n, zone=ZONE) for n in nodes]


class TestDeploy(testtools.TestCase):

    def test_generate_agents_alone_single_room(self):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'zone': ZONE,
                'node': 'dos'},
        }
        actual = deploy.generate_agents(nodes_helper('uno', 'dos'),
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
                'zone': ZONE,
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'zone': ZONE,
                'node': 'dos'},
        }
        actual = deploy.generate_agents(nodes_helper('uno', 'dos', 'tre'),
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
                'zone': ZONE,
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'mode': 'master',
                'node': 'dos',
                'zone': ZONE,
                'slave_id': 'UU1D_slave_1'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'mode': 'slave',
                'zone': ZONE,
                'node': 'dos'},
            'UU1D_master_2': {
                'id': 'UU1D_master_2',
                'mode': 'master',
                'node': 'tre',
                'zone': ZONE,
                'slave_id': 'UU1D_slave_2'},
            'UU1D_slave_2': {
                'id': 'UU1D_slave_2',
                'master_id': 'UU1D_master_2',
                'mode': 'slave',
                'zone': ZONE,
                'node': 'tre'},
        }
        actual = deploy.generate_agents(nodes_helper('uno', 'dos', 'tre'),
                                        ['pair', 'double_room'],
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_mixed_room(self):
        unique = 'UU1D'
        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'mode': 'master',
                'zone': ZONE,
                'node': 'uno',
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'zone': ZONE,
                'node': 'dos'},
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'mode': 'master',
                'zone': ZONE,
                'node': 'dos',
                'slave_id': 'UU1D_slave_1'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'mode': 'slave',
                'zone': ZONE,
                'node': 'uno'},
        }
        actual = deploy.generate_agents(nodes_helper('uno', 'dos'),
                                        ['pair', 'mixed_room'],
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_alone_single_room_double_density(self):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'zone': ZONE,
                'node': 'uno'},
        }
        actual = deploy.generate_agents(nodes_helper('uno'),
                                        ['single_room', {'density': 2}],
                                        unique)
        self.assertEqual(expected, actual)

    @mock.patch('random.sample')
    def test_generate_agents_alone_single_room_compute_nodes(self, mr):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'zone': ZONE,
                'node': 'duo'},
        }
        compute_nodes = nodes_helper('uno', 'duo', 'tre')
        mr.return_value = compute_nodes[:2]
        actual = deploy.generate_agents(compute_nodes,
                                        ['single_room', {'compute_nodes': 2}],
                                        unique)
        self.assertEqual(expected, actual)

    @mock.patch('random.sample')
    def test_generate_agents_alone_single_room_density_compute_nodes(self, mr):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'zone': ZONE,
                'node': 'uno'},
        }
        compute_nodes = nodes_helper('uno', 'duo', 'tre')
        mr.return_value = compute_nodes[:1]
        actual = deploy.generate_agents(compute_nodes,
                                        ['single_room', {'compute_nodes': 1},
                                         {'density': 2}],
                                        unique)
        self.assertEqual(expected, actual)

    @mock.patch('random.sample')
    def test_generate_agents_pair_single_room_density_compute_nodes(self, mr):
        unique = 'UU1D'
        compute_nodes = nodes_helper('uno', 'duo', 'tre')
        mr.return_value = compute_nodes[:2]
        actual = deploy.generate_agents(nodes_helper('uno', 'duo', 'tre'),
                                        ['pair', 'single_room',
                                         {'density': 4}, {'compute_nodes': 2}],
                                        unique)
        self.assertEqual(8, len(actual))

    def test_generate_agents_zones_specified(self):
        unique = 'UU1D'
        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'slave_id': 'UU1D_slave_0',
                'mode': 'master',
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'zone': ZONE,
                'node': 'tre'},
        }
        nodes = [
            {'host': 'uno', 'zone': ZONE},
            {'host': 'duo', 'zone': 'other-zone'},
            {'host': 'tre', 'zone': ZONE},
        ]
        actual = deploy.generate_agents(nodes,
                                        ['pair', 'single_room',
                                         {'zones': [ZONE]}],
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_cross_zones(self):
        unique = 'UU1D'
        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'slave_id': 'UU1D_slave_0',
                'mode': 'master',
                'zone': 'nova',
                'node': 'uno'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'zone': 'vcenter',
                'node': 'tre'},
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'slave_id': 'UU1D_slave_1',
                'mode': 'master',
                'zone': 'nova',
                'node': 'duo'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'mode': 'slave',
                'zone': 'vcenter',
                'node': 'cinco'},
        }
        nodes = [
            {'host': 'uno', 'zone': 'nova'},
            {'host': 'duo', 'zone': 'nova'},
            {'host': 'tre', 'zone': 'vcenter'},
            {'host': 'quattro', 'zone': 'nova'},
            {'host': 'cinco', 'zone': 'vcenter'},
        ]
        actual = deploy.generate_agents(
            nodes,
            ['pair', 'single_room', {'zones': ['nova', 'vcenter']},
             'cross_az'],
            unique)
        self.assertEqual(expected, actual)

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

    def test_filter_agents_pair_single_room_with_overrides(self):
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
        ips = {
            'UU1D_master_0': '10.0.0.2',
            'UU1D_slave_0': '10.0.0.4',
        }
        stack_outputs = {}
        expected = {'UU1D_master_0': agents['UU1D_master_0'],
                    'UU1D_slave_0': agents['UU1D_slave_0']}

        def override(agent):
            return dict(ip=ips[agent['id']])

        filtered = deploy.filter_agents(agents, stack_outputs,
                                        override=override)
        self.assertEqual(expected, filtered)
        self.assertEqual(filtered['UU1D_master_0']['ip'], ips['UU1D_master_0'])

    def test_prepare_for_cross_az(self):
        source = [
            dict(host='uno', zone='nova'),
            dict(host='duo', zone='nova'),
            dict(host='tre', zone='vcenter'),
        ]
        expected = [
            dict(host='uno', zone='nova'),
            dict(host='tre', zone='vcenter'),
        ]
        observed = deploy.prepare_for_cross_az(source, ['nova', 'vcenter'])
        self.assertEqual(expected, observed)
