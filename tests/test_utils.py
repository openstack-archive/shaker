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
import ast

import testtools

from shaker.engine import utils


class TestUtils(testtools.TestCase):
    def setUp(self):
        super(TestUtils, self).setUp()

    def test_split_address_valid(self):
        self.assertEqual(('10.0.0.1', '6777'),
                         utils.split_address('10.0.0.1:6777'))

    def test_split_address_invalid(self):
        self.assertRaises(ValueError, utils.split_address, 'erroneous')

    def test_flatten_dict(self):
        self.assertEqual({}, dict(utils.flatten_dict({})))
        self.assertEqual(
            {'pa_b': 1},
            dict(utils.flatten_dict({'a': {'b': 1}}, prefix='p', sep='_')))
        self.assertEqual(
            {'a': 1, 'b.c': 2, 'b.d': 3},
            dict(utils.flatten_dict({'a': 1, 'b': {'c': 2, 'd': 3}})))

    def test_eval(self):
        self.assertEqual(2 ** 6, utils.eval_expr('2**6'))
        self.assertEqual(True, utils.eval_expr('11 > a > 5', {'a': 7}))
        self.assertEqual(42, utils.eval_expr('2 + a.b', {'a': {'b': 40}}))
        self.assertEqual(True, utils.eval_expr('11 > 7 and 5 < 6'))
        self.assertEqual(False, utils.eval_expr('(not 11 > 7) or (not 5 < 6)'))

    def test_eval_sla(self):
        records = [{'type': 'agent', 'test': 'iperf_tcp',
                    'stats': {'bandwidth': {'mean': 700}}},
                   {'type': 'agent', 'test': 'iperf_udp',
                    'stats': {'bandwidth': {'mean': 1000}}},
                   {'type': 'node', 'test': 'iperf_tcp',
                    'stats': {'bandwidth': {'mean': 850}}}]

        sla_records = utils.eval_expr(
            '[type == "agent"] >> (stats.bandwidth.mean > 800)',
            records)
        self.assertEqual([(records[0], False), (records[1], True)],
                         sla_records)

        sla_records = utils.eval_expr(
            '[test == "iperf_udp", type == "node"] >> '
            '(stats.bandwidth.mean > 900)',
            records)
        self.assertEqual([(records[1], True), (records[2], False)],
                         sla_records)

    def test_dump_ast_node(self):
        self.assertEqual('(stats.bandwidth.mean > 900)', utils.dump_ast_node(
            ast.parse('stats.bandwidth.mean > 900', mode='eval')))

        expr = '(stats.bandwidth.mean > 900 and not stats.ping.min < 0.5)'
        self.assertEqual(expr,
                         utils.dump_ast_node(ast.parse(expr, mode='eval')))
