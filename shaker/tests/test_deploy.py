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
import os
import re
import testtools
import uuid

from oslo_config import cfg
from oslo_config import fixture as config_fixture_pkg
from shaker.engine import config
from shaker.engine import deploy
from shaker.engine import utils
from shaker.openstack.clients import heat
from shaker.openstack.clients import nova
from shaker.tests import fakes
from timeout_decorator import TimeoutError

ZONE = 'zone'


def nodes_helper(*nodes):
    return [dict(host=n, zone=ZONE) for n in nodes]


class TestDeploy(testtools.TestCase):
    def setUp(self):
        super(TestDeploy, self).setUp()

        conf = cfg.CONF
        self.addCleanup(conf.reset)
        self.config_fixture = self.useFixture(config_fixture_pkg.Config(conf))
        conf.register_opts(
            config.COMMON_OPTS + config.OPENSTACK_OPTS + config.SERVER_OPTS +
            config.REPORT_OPTS)

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

    def test_generate_agents_alone_single_room_az_host(self):
        unique = 'UU1D'
        expected = {
            'UU1D_agent_0': {
                'id': 'UU1D_agent_0',
                'mode': 'alone',
                'availability_zone': '%s:uno' % ZONE,
                'zone': ZONE,
                'node': 'uno'},
        }
        zones = ['%s:uno' % ZONE]
        accommodation = deploy.normalize_accommodation(
            ['single_room', {'zones': zones}])
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

    def test_generate_agents_pair_single_room_az_host(self):
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
        zones = ['%s:uno' % ZONE, '%s:dos' % ZONE]
        accommodation = deploy.normalize_accommodation(
            ['pair', 'single_room', {'zones': zones}])
        actual = deploy.generate_agents(nodes_helper('uno', 'dos', 'tre'),
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_single_room_not_enough(self):
        unique = 'UU1D'
        accommodation = deploy.normalize_accommodation(['pair', 'single_room'])
        self.assertRaises(deploy.DeploymentException, deploy.generate_agents,
                          ['uno'], accommodation, unique)

    def test_generate_agents_pair_single_room_best_effort(self):
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
        }
        accommodation = deploy.normalize_accommodation(
            ['pair', 'single_room', 'best_effort'])
        actual = deploy.generate_agents(nodes_helper('uno'),
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_single_room_best_effort_three_nodes(self):
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
        accommodation = deploy.normalize_accommodation(
            ['pair', 'single_room', 'best_effort'])
        actual = deploy.generate_agents(nodes_helper('uno', 'dos', 'tre'),
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

    def test_generate_agents_pair_single_room_compute_nodes_not_enough(self):
        unique = 'UU1D'
        accommodation = deploy.normalize_accommodation(
            ['pair', 'single_room', {'compute_nodes': 2}])
        self.assertRaises(deploy.DeploymentException, deploy.generate_agents,
                          ['uno'], accommodation, unique)

    def test_generate_agents_pair_single_room_compute_nodes_best_effort(self):
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
        }
        accommodation = deploy.normalize_accommodation(
            ['pair', 'single_room', 'best_effort', {'compute_nodes': 2}])
        actual = deploy.generate_agents(nodes_helper('uno'),
                                        accommodation,
                                        unique)
        self.assertEqual(expected, actual)

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

    def test_generate_agents_pair_double_room_az_host(self):
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
        }
        zones = ['%s:uno' % ZONE, '%s:dos' % ZONE]
        accommodation = deploy.normalize_accommodation(
            ['pair', 'double_room', {'zones': zones}])
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

    def test_generate_agents_alone_single_room_compute_nodes_not_enough(self):
        unique = 'UU1D'
        compute_nodes = nodes_helper('uno', 'duo')
        accommodation = deploy.normalize_accommodation(
            ['single_room', {'compute_nodes': 3}])
        self.assertRaises(deploy.DeploymentException, deploy.generate_agents,
                          compute_nodes, accommodation, unique)

    @mock.patch('random.sample')
    def test_generate_agents_alone_single_room_compute_nodes_best_effort(self,
                                                                         mr):
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
        compute_nodes = nodes_helper('uno', 'duo')
        mr.side_effect = lambda x, n: x[:n]
        accommodation = deploy.normalize_accommodation(
            ['single_room', 'best_effort', {'compute_nodes': 3}])
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
        agents = deployment.deploy(
            {'agents': [{'id': 'agent', 'mode': 'alone'}]})

        self.assertEqual(expected, agents)

    def test_deploy_template_error_when_non_initialized(self):
        deployment = deploy.Deployment()

        self.assertRaises(deploy.DeploymentException,
                          deployment.deploy, {'template': 'foo'})

    @mock.patch('shaker.openstack.clients.heat.get_stack_outputs')
    @mock.patch('shaker.openstack.clients.heat.create_stack')
    @mock.patch('shaker.openstack.clients.openstack.OpenStackClient')
    @mock.patch('shaker.engine.deploy.Deployment._get_compute_nodes')
    def test_deploy_from_hot_with_env_file(self, nova_nodes_mock,
                                           openstack_mock, create_stack_mock,
                                           stack_output_mock):
        test_file = 'shaker/scenarios/test/sample_with_env.yaml'
        absolute_path = utils.resolve_relative_path(test_file)
        scenario = utils.read_yaml_file(absolute_path)

        stack_name = 'shaker_abcdefg'

        server_endpoint = "127.0.0.01"
        base_dir = os.path.dirname(absolute_path)

        deployment = deploy.Deployment()
        deployment.stack_name = stack_name
        deployment.external_net = 'test-external_net'
        deployment.image_name = 'test-image'
        deployment.flavor_name = 'test-flavor'
        deployment.dns_nameservers = '8.8.8.8'
        deployment.openstack_client = openstack_mock

        # read the env file to determine what cidr is set to
        # minus the last digit
        env_file = utils.read_file(scenario['deployment']['env_file'],
                                   base_dir)
        cidr = re.findall(r'[0-9]+(?:\.[0-9]+){2}', env_file)[0]

        nova_nodes_mock.return_value = [{'host': 'host-1', 'zone': 'nova'}]

        create_stack_mock.return_value = uuid.uuid4()

        heat_outputs = {
            stack_name + '_master_0_instance_name': 'instance-0000052f',
            stack_name + '_master_0_ip': '192.0.0.3',
            stack_name + '_slave_0_ip': '192.0.0.4',
            stack_name + '_slave_0_instance_name': 'instance-0000052c'}

        stack_output_mock.return_value = heat_outputs

        expected = {
            'shaker_abcdefg_master_0': {'availability_zone': 'nova:host-1',
                                        'id': 'shaker_abcdefg_master_0',
                                        'ip': cidr + '.3',
                                        'mode': 'master',
                                        'node': 'host-1',
                                        'slave_id': 'shaker_abcdefg_slave_0',
                                        'zone': 'nova'},
            'shaker_abcdefg_slave_0': {'availability_zone': 'nova:host-1',
                                       'id': 'shaker_abcdefg_slave_0',
                                       'ip': cidr + '.4',
                                       'master_id': 'shaker_abcdefg_master_0',
                                       'mode': 'slave',
                                       'node': 'host-1',
                                       'zone': 'nova'}}

        agents = deployment._deploy_from_hot(scenario['deployment'],
                                             server_endpoint,
                                             base_dir=base_dir)

        self.assertEqual(expected, agents)

    @mock.patch('shaker.openstack.clients.heat.get_stack_outputs')
    @mock.patch('shaker.openstack.clients.heat.create_stack')
    @mock.patch('shaker.openstack.clients.openstack.OpenStackClient')
    @mock.patch('shaker.engine.deploy.Deployment._get_compute_nodes')
    def test_deploy_from_hot_with_support_stacks(self, nova_nodes_mock,
                                                 openstack_mock,
                                                 create_stack_mock,
                                                 stack_output_mock):
        test_file = 'shaker/scenarios/test/sample_with_support_stacks.yaml'
        absolute_path = utils.resolve_relative_path(test_file)
        scenario = utils.read_yaml_file(absolute_path)

        stack_name = 'shaker_abcdefg'

        server_endpoint = "127.0.0.01"
        base_dir = os.path.dirname(absolute_path)

        deployment = deploy.Deployment()
        deployment.stack_name = stack_name
        deployment.external_net = 'test-external_net'
        deployment.image_name = 'test-image'
        deployment.flavor_name = 'test-flavor'
        deployment.dns_nameservers = '8.8.8.8'
        deployment.openstack_client = openstack_mock

        nova_nodes_mock.return_value = [{'host': 'host-1', 'zone': 'nova'}]

        create_stack_mock.return_value = uuid.uuid4()

        heat_outputs = {
            stack_name + '_master_0_instance_name': 'instance-0000052f',
            stack_name + '_master_0_ip': '10.0.0.3',
            stack_name + '_slave_0_ip': '10.0.0.4',
            stack_name + '_slave_0_instance_name': 'instance-0000052c'}

        stack_output_mock.return_value = heat_outputs

        expected = {
            'shaker_abcdefg_master_0': {'availability_zone': 'nova:host-1',
                                        'id': 'shaker_abcdefg_master_0',
                                        'ip': '10.0.0.3',
                                        'mode': 'master',
                                        'node': 'host-1',
                                        'slave_id': 'shaker_abcdefg_slave_0',
                                        'zone': 'nova'},
            'shaker_abcdefg_slave_0': {'availability_zone': 'nova:host-1',
                                       'id': 'shaker_abcdefg_slave_0',
                                       'ip': '10.0.0.4',
                                       'master_id': 'shaker_abcdefg_master_0',
                                       'mode': 'slave',
                                       'node': 'host-1',
                                       'zone': 'nova'}}

        agents = deployment._deploy_from_hot(scenario['deployment'],
                                             server_endpoint,
                                             base_dir=base_dir)

        self.assertEqual(create_stack_mock.call_count, 3)
        self.assertEqual(expected, agents)

    @mock.patch('shaker.openstack.clients.heat.create_stack')
    @mock.patch('shaker.openstack.clients.openstack.OpenStackClient')
    def test_deploy_support_stacks(self, openstack_mock, create_stack_mock):
        test_file = 'shaker/scenarios/test/sample_with_support_stacks.yaml'
        absolute_path = utils.resolve_relative_path(test_file)
        scenario = utils.read_yaml_file(absolute_path)

        support_stacks = scenario['deployment']['support_templates']
        base_dir = os.path.dirname(absolute_path)

        deployment = deploy.Deployment()
        deployment.stack_name = 'shaker_abcdefg'
        deployment.openstack_client = openstack_mock

        support_stack_1 = uuid.uuid4()
        support_stack_2 = uuid.uuid4()

        create_stack_mock.side_effect = (support_stack_1, support_stack_2)

        deployment._deploy_support_stacks(support_stacks, base_dir)

        self.assertEqual(support_stack_1, deployment.support_stacks[0].id)
        self.assertEqual(support_stack_2, deployment.support_stacks[1].id)

    @mock.patch('shaker.openstack.clients.heat.create_stack')
    @mock.patch('shaker.openstack.clients.openstack.OpenStackClient')
    def test_deploy_support_stacks_with_conflict(self, openstack_mock,
                                                 create_stack_mock):
        test_file = 'shaker/scenarios/test/sample_with_support_stacks.yaml'
        absolute_path = utils.resolve_relative_path(test_file)
        scenario = utils.read_yaml_file(absolute_path)

        support_stacks = scenario['deployment']['support_templates']
        base_dir = os.path.dirname(absolute_path)

        deployment = deploy.Deployment()
        deployment.stack_name = 'shaker_abcdefg'
        deployment.openstack_client = openstack_mock

        support_stack_1 = heat.exc.Conflict
        support_stack_2 = uuid.uuid4()

        create_stack_mock.side_effect = (support_stack_1, support_stack_2)

        deployment._deploy_support_stacks(support_stacks, base_dir)

        self.assertEqual(support_stack_2, deployment.support_stacks[0].id)
        self.assertEqual(create_stack_mock.call_count, 2)

    @mock.patch('shaker.openstack.clients.heat.get_stack_status')
    @mock.patch('shaker.openstack.clients.openstack.OpenStackClient')
    def test_wait_stack_deletion(self, openstack_mock, get_status_mock):
        get_status_mock.side_effect = heat.exc.HTTPNotFound
        stack_id = uuid.uuid4()

        self.assertIsNone(heat.wait_stack_deletion(openstack_mock, stack_id))

    @mock.patch('shaker.openstack.clients.heat.get_stack_status')
    @mock.patch('shaker.openstack.clients.openstack.OpenStackClient')
    def test_wait_stack_deletion_failed_stack(self, openstack_mock,
                                              get_status_mock):
        get_status_mock.return_value = ('FAILED', 'some_reason')
        stack_id = uuid.uuid4()
        self.assertRaises(heat.exc.StackFailure, heat.wait_stack_deletion,
                          openstack_mock, stack_id)

    @mock.patch('shaker.openstack.clients.heat.get_stack_status')
    @mock.patch('shaker.openstack.clients.openstack.OpenStackClient')
    def test_wait_stack_deletion_timeout(self, openstack_mock,
                                         get_status_mock):
        get_status_mock.side_effect = TimeoutError
        stack_id = uuid.uuid4()

        self.assertIsNone(heat.wait_stack_deletion(openstack_mock, stack_id))

    @mock.patch('shaker.openstack.clients.openstack.OpenStackClient')
    def test_get_compute_nodes_flavor_no_extra_specs(self,
                                                     nova_client_mock):
        # setup fake nova api service list response
        compute_host_1 = fakes.FakeNovaServiceList(host='host-1')
        compute_host_2 = fakes.FakeNovaServiceList(host='host-2')
        compute_host_3 = fakes.FakeNovaServiceList(host='host-3')

        nova_client_mock.nova.services.list.return_value = [compute_host_1,
                                                            compute_host_2,
                                                            compute_host_3]

        # setup fake nova api flavor list response
        flavor_no_exta_specs = fakes.FakeNovaFlavorList(
            name='flavor_no_exta_specs')

        nova_client_mock.nova.flavors.list.return_value = [
            flavor_no_exta_specs]

        deployment = deploy.Deployment()
        deployment.flavor_name = 'flavor_no_exta_specs'
        deployment.openstack_client = nova_client_mock

        accommodation = {'compute_nodes': 3}
        expected = [{'host': 'host-1', 'zone': 'nova'},
                    {'host': 'host-2', 'zone': 'nova'},
                    {'host': 'host-3', 'zone': 'nova'}]

        observed = deployment._get_compute_nodes(accommodation)

        self.assertEqual(expected, observed)

    @mock.patch('shaker.openstack.clients.openstack.OpenStackClient')
    def test_get_compute_nodes_flavor_extra_specs_no_match(self,
                                                           nova_client_mock):
        # setup fake nova api service list response
        compute_host_1 = fakes.FakeNovaServiceList(host='host-1')
        compute_host_2 = fakes.FakeNovaServiceList(host='host-2')
        compute_host_3 = fakes.FakeNovaServiceList(host='host-3')

        nova_client_mock.nova.services.list.return_value = [compute_host_1,
                                                            compute_host_2,
                                                            compute_host_3]

        # setup fake nova api flavor list response
        flavor_with_extra_specs = fakes.FakeNovaFlavorList(
            name='flavor_with_extra_specs',
            extra_specs={'aggregate_instance_extra_specs:other_hw': 'false'})

        nova_client_mock.nova.flavors.list.return_value = [
            flavor_with_extra_specs]

        # setup fake nova api aggregate list response
        agg_host_1 = fakes.FakeNovaAggregateList(hosts=['host-1'], metadata={
            'special_hw': 'true'})
        agg_host_2 = fakes.FakeNovaAggregateList(hosts=['host-2'])
        agg_host_3 = fakes.FakeNovaAggregateList(hosts=['host-3'])

        nova_client_mock.nova.aggregates.list.return_value = [agg_host_1,
                                                              agg_host_2,
                                                              agg_host_3]

        deployment = deploy.Deployment()
        deployment.flavor_name = 'flavor_with_extra_specs'
        deployment.openstack_client = nova_client_mock

        accommodation = {'compute_nodes': 3}
        expected = []

        observed = deployment._get_compute_nodes(accommodation)

        self.assertEqual(expected, observed)

    @mock.patch('shaker.openstack.clients.openstack.OpenStackClient')
    def test_get_compute_nodes_flavor_extra_specs_with_match(self,
                                                             nova_client_mock):
        # setup fake nova api service list response
        compute_host_1 = fakes.FakeNovaServiceList(host='host-1')
        compute_host_2 = fakes.FakeNovaServiceList(host='host-2')
        compute_host_3 = fakes.FakeNovaServiceList(host='host-3')

        nova_client_mock.nova.services.list.return_value = [compute_host_1,
                                                            compute_host_2,
                                                            compute_host_3]

        # setup fake nova api flavor list response
        flavor_with_extra_specs = fakes.FakeNovaFlavorList(
            name='flavor_with_extra_specs',
            extra_specs={'aggregate_instance_extra_specs:special_hw': 'true'})

        nova_client_mock.nova.flavors.list.return_value = [
            flavor_with_extra_specs]

        # setup fake nova api aggregate list response
        agg_host_1 = fakes.FakeNovaAggregateList(hosts=['host-1'])
        agg_host_2 = fakes.FakeNovaAggregateList(hosts=['host-2'], metadata={
            'special_hw': 'true'})
        agg_host_3 = fakes.FakeNovaAggregateList(hosts=['host-3'])

        nova_client_mock.nova.aggregates.list.return_value = [agg_host_1,
                                                              agg_host_2,
                                                              agg_host_3]

        deployment = deploy.Deployment()
        deployment.flavor_name = 'flavor_with_extra_specs'
        deployment.openstack_client = nova_client_mock

        accommodation = {'compute_nodes': 3}
        expected = [{'host': 'host-2', 'zone': 'nova'}]

        observed = deployment._get_compute_nodes(accommodation)

        self.assertEqual(expected, observed)

    @mock.patch('shaker.openstack.clients.nova.get_available_compute_nodes')
    def test_get_compute_nodes_non_admin(self, nova_nodes_mock):
        deployment = deploy.Deployment()
        deployment.flavor_name = 'test.flavor'
        deployment.openstack_client = mock.Mock()

        def raise_error(nova_client, flavor_name):
            raise nova.ForbiddenException('err')

        nova_nodes_mock.side_effect = raise_error
        accommodation = {'compute_nodes': 4}
        expected = list(itertools.repeat({'host': None, 'zone': 'nova'}, 4))

        observed = deployment._get_compute_nodes(accommodation)

        self.assertEqual(expected, observed)

    @mock.patch('shaker.openstack.clients.nova.get_available_compute_nodes')
    def test_get_compute_nodes_non_admin_zones(self, nova_nodes_mock):
        deployment = deploy.Deployment()
        deployment.flavor_name = 'test.flavor'
        deployment.openstack_client = mock.Mock()

        def raise_error(nova_client, flavor_name):
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
        deployment.flavor_name = 'test.flavor'
        deployment.openstack_client = mock.Mock()

        def raise_error(nova_client, flavor_name):
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

    def test_override_single_scenario_availability_zone(self):
        origin = ['pair', {'zones': ['nova']}]

        self.config_fixture.config(scenario_availability_zone='test')

        expected = collections.OrderedDict()
        expected['pair'] = True
        expected['zones'] = ['test']

        self.assertEqual(expected, deploy.normalize_accommodation(origin))

    def test_override_list_scenario_availability_zone(self):
        origin = ['pair', {'zones': ['nova']}]

        self.config_fixture.config(scenario_availability_zone='test1, test2')

        expected = collections.OrderedDict()
        expected['pair'] = True
        expected['zones'] = ['test1', 'test2']

        self.assertEqual(expected, deploy.normalize_accommodation(origin))

    def test_override_scenario_compute_nodes(self):
        origin = ['pair', {'compute_nodes': 1}]

        self.config_fixture.config(scenario_compute_nodes=5)

        expected = collections.OrderedDict()
        expected['pair'] = True
        expected['compute_nodes'] = 5

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
