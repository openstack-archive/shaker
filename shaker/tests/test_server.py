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
from oslo_config import cfg
from oslo_config import fixture as config_fixture_pkg
from oslotest import mockpatch
import testtools

from shaker.engine import config
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
                  for arr in server._pick_agents(agents, None)]
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
                  for arr in server._pick_agents(agents, None)]
        self.assertEqual([set('master_%s' % i for i in range(10))],
                         picked)

    def test_pick_agents_linear(self):
        agents = {}
        for i in range(10):
            agents[i] = {
                'id': i, 'mode': 'alone', 'node': 'uno',
            }
        picked = [set(a['id'] for a in arr)
                  for arr in server._pick_agents(agents, 'linear')]
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
                                                 'quadratic')]
        self.assertEqual([set(range(1)), set(range(2)),
                          set(range(5)), set(range(10))],
                         picked)


class TestServerPlayScenario(testtools.TestCase):

    scenario_file_name = 'folder/filename.yaml'
    deployment = {}
    scenario = {
        'title': 'Hamlet',
        'deployment': deployment,
        'file_name': scenario_file_name,
        'execution': {
            'tests': []
        }
    }

    def setUp(self):
        super(TestServerPlayScenario, self).setUp()

        conf = cfg.CONF
        self.addCleanup(conf.reset)
        self.config_fixture = self.useFixture(config_fixture_pkg.Config(conf))
        conf.register_opts(
            config.COMMON_OPTS + config.OPENSTACK_OPTS + config.SERVER_OPTS +
            config.REPORT_OPTS)

        self.config_fixture.config(server_endpoint='127.0.0.1:5999')
        self.config_fixture.config(scenario=self.scenario_file_name)

        self.useFixture(mockpatch.Patch('shaker.engine.quorum.make_quorum'))

    def assertContainsSimilarRecord(self, expected, output):
        has = False
        for actual in output['records'].values():
            has |= all(item in actual.items() for item in expected.items())
        s = 'Output should contain record similar to: %s' % expected
        self.assertTrue(has, msg=s)

    def assertNotContainsSimilarRecord(self, expected, output):
        has = False
        for actual in output['records'].values():
            has |= all(item in actual.items() for item in expected.items())
        s = 'Output should not contain record similar to: %s' % expected
        self.assertFalse(has, msg=s)

    @mock.patch('shaker.engine.server.execute')
    @mock.patch('shaker.engine.deploy.Deployment')
    def test_play_scenario(self, deploy_clz_mock, execute_mock):
        deploy_obj = mock.Mock()
        deploy_clz_mock.return_value = deploy_obj

        def _execute(output, quorum, execution, agents, matrix=None):
            output['records'].update({'UUID': {'id': 'UUID', 'status': 'ok'}})

        execute_mock.side_effect = _execute

        deploy_obj.deploy.return_value = {
            'ID': {'id': 'ID', 'mode': 'alone'}
        }

        # act!
        output = server.play_scenario(mock.MagicMock, self.scenario)

        self.assertNotContainsSimilarRecord({'status': 'error'}, output)
        self.assertContainsSimilarRecord({
            'status': 'ok', 'id': 'UUID', 'scenario': self.scenario['title']},
            output)

        deploy_obj.deploy.assert_called_once_with(
            self.deployment, base_dir='folder',
            server_endpoint='127.0.0.1:5999')
        deploy_obj.cleanup.assert_called_once_with()

    @mock.patch('shaker.engine.deploy.Deployment')
    def test_play_scenario_with_openstack(self, deploy_clz_mock):
        deploy_obj = mock.Mock()
        deploy_clz_mock.return_value = deploy_obj
        self.config_fixture.config(os_username='user')
        self.config_fixture.config(os_password='password')
        self.config_fixture.config(os_tenant_name='tenant')
        self.config_fixture.config(os_auth_url='auth-url')

        deploy_obj.deploy.return_value = {
            'ID': {'id': 'ID', 'mode': 'alone'}
        }

        # act!
        output = server.play_scenario(mock.MagicMock, self.scenario)

        self.assertNotContainsSimilarRecord({'status': 'error'}, output)

        deploy_obj.deploy.assert_called_once_with(
            self.deployment, base_dir='folder',
            server_endpoint='127.0.0.1:5999')
        openstack_params = dict(
            auth=dict(username='user', password='password',
                      tenant_name='tenant', auth_url='auth-url'),
            os_region_name='RegionOne',
            os_cacert=None, os_insecure=False)
        deploy_obj.connect_to_openstack.assert_called_once_with(
            openstack_params, 'shaker-flavor', 'shaker-image', None,
            ['8.8.8.8', '8.8.4.4'])
        deploy_obj.cleanup.assert_called_once_with()

    @mock.patch('shaker.engine.deploy.Deployment')
    def test_play_scenario_no_agents(self, deploy_clz_mock):
        deploy_obj = mock.Mock()
        deploy_clz_mock.return_value = deploy_obj

        deploy_obj.deploy.return_value = {}

        # act!
        output = server.play_scenario(mock.MagicMock, self.scenario)

        self.assertEqual(1, len(output['records']))
        self.assertContainsSimilarRecord({'status': 'error'}, output)

        deploy_obj.deploy.assert_called_once_with(
            self.deployment, base_dir='folder',
            server_endpoint='127.0.0.1:5999')
        deploy_obj.cleanup.assert_called_once_with()

    @mock.patch('shaker.engine.deploy.Deployment')
    def test_play_scenario_interrupted(self, deploy_clz_mock):
        deploy_obj = mock.Mock()
        deploy_clz_mock.return_value = deploy_obj

        deploy_obj.deploy.side_effect = KeyboardInterrupt

        # act!
        output = server.play_scenario(mock.MagicMock, self.scenario)

        self.assertEqual(1, len(output['records']))
        self.assertContainsSimilarRecord({'status': 'interrupted'}, output)

        deploy_obj.deploy.assert_called_once_with(
            self.deployment, base_dir='folder',
            server_endpoint='127.0.0.1:5999')
        deploy_obj.cleanup.assert_called_once_with()


class TestServerExecute(testtools.TestCase):

    @mock.patch('shaker.engine.utils.make_record_id', return_value='UUID')
    def test_execute(self, mri_mock):
        output = dict(records={}, tests={})
        quorum = mock.Mock()
        quorum.execute.return_value = {'the-agent': {'status': 'ok'}}
        execution = {'tests': [{'title': 'tcp', 'class': 'iperf'}]}
        agents = {'the-agent': {'id': 'the-agent', 'mode': 'alone'}}

        server.execute(output, quorum, execution, agents)

        expected_records = {
            'UUID': {
                'agent': 'the-agent', 'concurrency': 1, 'executor': 'iperf',
                'id': 'UUID', 'node': None, 'status': 'ok', 'test': 'tcp',
                'type': 'agent'
            }
        }
        expected_tests = {
            'tcp': {'title': 'tcp', 'class': 'iperf'}
        }

        self.assertEqual(expected_records, output['records'])
        self.assertEqual(expected_tests, output['tests'])

    @mock.patch('shaker.engine.utils.make_record_id', return_value='UUID')
    def test_execute_interrupted(self, mri_mock):
        output = dict(records={}, tests={})
        quorum = mock.Mock()
        quorum.execute.return_value = {'the-agent': {'status': 'interrupted'}}
        execution = {'tests': [{'title': 'tcp', 'class': 'iperf'},
                               {'title': 'udp', 'class': 'netperf'}]}
        agents = {'the-agent': {'id': 'the-agent', 'mode': 'alone'}}

        server.execute(output, quorum, execution, agents)

        expected_records = {
            'UUID': {
                'agent': 'the-agent', 'concurrency': 1, 'executor': 'iperf',
                'id': 'UUID', 'node': None, 'status': 'interrupted',
                'test': 'tcp', 'type': 'agent'
            }
        }
        expected_tests = {
            'tcp': {'title': 'tcp', 'class': 'iperf'}
        }

        self.assertEqual(expected_records, output['records'])
        self.assertEqual(expected_tests, output['tests'])
