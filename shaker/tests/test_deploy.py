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

import collections
import copy
import itertools
import mock
import testtools

from shaker.engine import deploy
from shaker.openstack.clients import nova

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
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'availability_zone': '%s:dos' % ZONE,
                'zone': ZONE,
                'node': 'dos'},
        }
        accommodation = deploy.normalize_accommodation(['single_room'])
        actual = deploy.generate_agents(nodes_helper('uno', 'dos'),
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_single_room(self):
        unique = 'UU1D'
        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'mode': 'master',
                'availability_zone': '%s:uno' % ZONE,
                'node': 'uno',
                'zone': ZONE,
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'availability_zone': '%s:dos' % ZONE,
                'zone': ZONE,
                'node': 'dos'},
        }
        accommodation = deploy.normalize_accommodation(['pair', 'single_room'])
        actual = deploy.generate_agents(nodes_helper('uno', 'dos', 'tre'),
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_single_room_not_enough(self):
        unique = 'UU1D'
        accommodation = deploy.normalize_accommodation(['pair', 'single_room'])
        self.assertRaises(deploy.DeploymentException, deploy.generate_agents,
                          ['uno'], accommodation, unique)

    def test_generate_agents_pair_double_room(self):
        unique = 'UU1D'
        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'mode': 'master',
                'availability_zone': '%s:uno' % ZONE,
                'node': 'uno',
                'zone': ZONE,
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'mode': 'master',
                'availability_zone': '%s:dos' % ZONE,
                'node': 'dos',
                'zone': ZONE,
                'slave_id': 'UU1D_slave_1'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'mode': 'slave',
                'availability_zone': '%s:dos' % ZONE,
                'zone': ZONE,
                'node': 'dos'},
            'UU1D_master_2': {
                'id': 'UU1D_master_2',
                'mode': 'master',
                'availability_zone': '%s:tre' % ZONE,
                'node': 'tre',
                'zone': ZONE,
                'slave_id': 'UU1D_slave_2'},
            'UU1D_slave_2': {
                'id': 'UU1D_slave_2',
                'master_id': 'UU1D_master_2',
                'mode': 'slave',
                'availability_zone': '%s:tre' % ZONE,
                'zone': ZONE,
                'node': 'tre'},
        }
        accommodation = deploy.normalize_accommodation(['pair', 'double_room'])
        actual = deploy.generate_agents(nodes_helper('uno', 'dos', 'tre'),
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_mixed_room(self):
        unique = 'UU1D'
        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'mode': 'master',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno',
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'availability_zone': '%s:dos' % ZONE,
                'zone': ZONE,
                'node': 'dos'},
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'mode': 'master',
                'availability_zone': '%s:dos' % ZONE,
                'zone': ZONE,
                'node': 'dos',
                'slave_id': 'UU1D_slave_1'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'mode': 'slave',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
        }
        accommodation = deploy.normalize_accommodation(['pair', 'mixed_room'])
        actual = deploy.generate_agents(nodes_helper('uno', 'dos'),
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_alone_single_room_double_density(self):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
        }
        accommodation = deploy.normalize_accommodation(
            ['single_room', {'density': 2}])
        actual = deploy.generate_agents(nodes_helper('uno'),
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    @mock.patch('random.sample')
    def test_generate_agents_alone_single_room_compute_nodes(self, mr):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'availability_zone': '%s:duo' % ZONE,
                'zone': ZONE,
                'node': 'duo'},
        }
        compute_nodes = nodes_helper('uno', 'duo', 'tre')
        mr.side_effect = lambda x, n: x[:n]
        accommodation = deploy.normalize_accommodation(
            ['single_room', {'compute_nodes': 2}])
        actual = deploy.generate_agents(compute_nodes,
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    @mock.patch('random.sample')
    def test_generate_agents_alone_single_room_density_compute_nodes(self, mr):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_agent_1': {
                'id': 'UU1D_agent_1',
                'mode': 'alone',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
        }
        compute_nodes = nodes_helper('uno', 'duo', 'tre')
        mr.side_effect = lambda x, n: x[:n]
        accommodation = deploy.normalize_accommodation(
            ['single_room', {'compute_nodes': 1}, {'density': 2}])
        actual = deploy.generate_agents(compute_nodes,
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    @mock.patch('random.sample')
    def test_generate_agents_pair_single_room_density_compute_nodes(self, mr):
        unique = 'UU1D'
        compute_nodes = nodes_helper('uno', 'duo', 'tre')
        mr.side_effect = lambda x, n: x[:n]
        accommodation = deploy.normalize_accommodation(
            ['pair', 'single_room', {'density': 4}, {'compute_nodes': 2}])
        actual = deploy.generate_agents(compute_nodes,
                                        accommodation,
                                        unique)
        self.assertEqual(8, len(actual))

    def test_generate_agents_zones_specified(self):
        unique = 'UU1D'
        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'slave_id': 'UU1D_slave_0',
                'mode': 'master',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'availability_zone': '%s:tre' % ZONE,
                'zone': ZONE,
                'node': 'tre'},
        }
        nodes = [
            {'host': 'uno', 'zone': ZONE},
            {'host': 'duo', 'zone': 'other-zone'},
            {'host': 'tre', 'zone': ZONE},
        ]
        accommodation = deploy.normalize_accommodation(
            ['pair', 'single_room', {'zones': [ZONE]}])
        actual = deploy.generate_agents(nodes,
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    @mock.patch('random.sample')
    def test_generate_agents_zones_and_compute_nodes_specified(self, mr):
        mr.side_effect = lambda x, n: x[:n]
        unique = 'UU1D'
        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'slave_id': 'UU1D_slave_0',
                'mode': 'master',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'availability_zone': '%s:tre' % ZONE,
                'zone': ZONE,
                'node': 'tre'},
        }
        nodes = [
            {'host': 'uno', 'zone': ZONE},
            {'host': 'duo', 'zone': 'other-zone'},
            {'host': 'tre', 'zone': ZONE},
            {'host': 'cuattro', 'zone': ZONE},
            {'host': 'cinco', 'zone': ZONE},
        ]
        accommodation = deploy.normalize_accommodation(
            ['pair', 'single_room', {'zones': [ZONE]}, {'compute_nodes': 2}])
        actual = deploy.generate_agents(nodes,
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_cross_zones(self):
        unique = 'UU1D'
        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'slave_id': 'UU1D_slave_0',
                'mode': 'master',
                'availability_zone': 'nova:uno',
                'zone': 'nova',
                'node': 'uno'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'mode': 'slave',
                'availability_zone': 'vcenter:tre',
                'zone': 'vcenter',
                'node': 'tre'},
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'slave_id': 'UU1D_slave_1',
                'mode': 'master',
                'availability_zone': 'nova:duo',
                'zone': 'nova',
                'node': 'duo'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'mode': 'slave',
                'availability_zone': 'vcenter:cinco',
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
        accommodation = deploy.normalize_accommodation(
            ['pair', 'single_room', {'zones': ['nova', 'vcenter']},
             'cross_az'])
        actual = deploy.generate_agents(nodes, accommodation, unique)
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

    # Deployment class unit tests

    def test_deploy_local(self):
        deployment = deploy.Deployment()

        expected = {
            'local': {'id': 'local', 'mode': 'alone', 'node': 'localhost'}
        }
        agents = deployment.deploy({})

        self.assertEqual(expected, agents)

    def test_deploy_static(self):
        deployment = deploy.Deployment()

        expected = {
            'agent': {'id': 'agent', 'mode': 'alone'}
        }
        agents = deployment.deploy({'agents':
                                    [{'id': 'agent', 'mode': 'alone'}]})

        self.assertEqual(expected, agents)

    def test_deploy_template_error_when_non_initialized(self):
        deployment = deploy.Deployment()

        self.assertRaises(deploy.DeploymentException,
                          deployment.deploy, {'template': 'foo'})

    @mock.patch('shaker.openstack.clients.nova.get_available_compute_nodes')
    def test_get_compute_nodes_non_admin(self, nova_nodes_mock):
        deployment = deploy.Deployment()
        deployment.openstack_client = mock.Mock()

        def raise_error(arg):
            raise nova.ForbiddenException('err')

        nova_nodes_mock.side_effect = raise_error
        accommodation = {'compute_nodes': 4}
        expected = list(itertools.repeat({'host': None, 'zone': 'nova'}, 4))

        observed = deployment._get_compute_nodes(accommodation)

        self.assertEqual(expected, observed)

    @mock.patch('shaker.openstack.clients.nova.get_available_compute_nodes')
    def test_get_compute_nodes_non_admin_zones(self, nova_nodes_mock):
        deployment = deploy.Deployment()
        deployment.openstack_client = mock.Mock()

        def raise_error(arg):
            raise nova.ForbiddenException('err')

        nova_nodes_mock.side_effect = raise_error
        accommodation = {'compute_nodes': 4, 'zones': ['nova', 'nsx']}
        expected = [
            {'host': None, 'zone': 'nova'},
            {'host': None, 'zone': 'nsx'},
            {'host': None, 'zone': 'nova'},
            {'host': None, 'zone': 'nsx'},
        ]

        observed = deployment._get_compute_nodes(accommodation)

        self.assertEqual(expected, observed)

    @mock.patch('shaker.openstack.clients.nova.get_available_compute_nodes')
    def test_get_compute_nodes_non_admin_not_configured(self, nova_nodes_mock):
        deployment = deploy.Deployment()
        deployment.openstack_client = mock.Mock()

        def raise_error(arg):
            raise nova.ForbiddenException('err')

        nova_nodes_mock.side_effect = raise_error
        accommodation = {}

        self.assertRaises(deploy.DeploymentException,
                          deployment._get_compute_nodes, accommodation)

    def test_normalize_accommodation(self):
        origin = ['pair', 'single_room', {'compute_nodes': 2}]

        expected = collections.OrderedDict()
        expected['pair'] = True
        expected['single_room'] = True
        expected['compute_nodes'] = 2

        self.assertEqual(expected, deploy.normalize_accommodation(origin))

    def test_distribute_agents(self):
        agents = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'mode': 'master',
                'ip': '10.0.0.3',
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'ip': '10.0.0.4',
                'mode': 'slave'},
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'mode': 'master',
                'ip': '10.0.0.5',
                'slave_id': 'UU1D_slave_1'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'ip': '10.0.0.6',
                'mode': 'slave'},
        }
        hosts = {
            'UU1D_master_0': '001',
            'UU1D_slave_0': '002',
            'UU1D_master_1': '003',
            'UU1D_slave_1': '004',
        }

        expected = copy.deepcopy(agents)
        for k, v in hosts.items():
            expected[k]['node'] = v

        observed = deploy.distribute_agents(agents, lambda x: hosts[x])

        # expected no changes
        self.assertEqual(agents, observed)

    # todo refactor code to use lists instead of dicts
    def _test_distribute_agents_collision(self):
        agents = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'mode': 'master',
                'ip': '10.0.0.3',
                'slave_id': 'UU1D_slave_0'},
            'UU1D_slave_0': {
                'id': 'UU1D_slave_0',
                'master_id': 'UU1D_master_0',
                'ip': '10.0.0.4',
                'mode': 'slave'},
            'UU1D_master_1': {
                'id': 'UU1D_master_1',
                'mode': 'master',
                'ip': '10.0.0.5',
                'slave_id': 'UU1D_slave_1'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_1',
                'ip': '10.0.0.6',
                'mode': 'slave'},
        }
        hosts = {
            'UU1D_master_0': '001',
            'UU1D_slave_0': '001',  # collides with master_0
            'UU1D_master_1': '003',
            'UU1D_slave_1': '004',
        }

        expected = {
            'UU1D_master_0': {
                'id': 'UU1D_master_0',
                'mode': 'master',
                'ip': '10.0.0.3',
                'node': '001',
                'slave_id': 'UU1D_slave_1'},
            'UU1D_slave_1': {
                'id': 'UU1D_slave_1',
                'master_id': 'UU1D_master_0',
                'ip': '10.0.0.6',
                'node': '004',
                'mode': 'slave'},
        }

        observed = deploy.distribute_agents(agents, lambda x: hosts[x])

        self.assertEqual(expected, observed)
