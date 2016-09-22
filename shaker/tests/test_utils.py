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

    @mock.patch('os.walk')
    @mock.patch('shaker.engine.utils.resolve_relative_path')
    def test_make_help_options(self, resolve_mock, walk_mock):
        base_dir = 'abc/def'
        abs_dir = '/files/' + base_dir
        walk_mock.side_effect = [
            [(abs_dir, [], ['klm.yaml']), (abs_dir, [], ['ijk.yaml'])],
        ]
        resolve_mock.side_effect = [abs_dir]

        expected = 'List: "ijk", "klm"'
        observed = utils.make_help_options('List: %s', base_dir)
        self.assertEqual(expected, observed)

    @mock.patch('os.walk')
    @mock.patch('shaker.engine.utils.resolve_relative_path')
    def test_make_help_options_subdir(self, resolve_mock, walk_mock):
        base_dir = 'abc/def'
        abs_dir = '/files/' + base_dir
        walk_mock.side_effect = [
            [(abs_dir + '/sub', [], ['klm.yaml']),
             (abs_dir + '/sub', [], ['ijk.yaml'])],
        ]
        resolve_mock.side_effect = [abs_dir]

        expected = 'List: "sub/ijk", "sub/klm"'
        observed = utils.make_help_options('List: %s', base_dir)
        self.assertEqual(expected, observed)

    @mock.patch('os.walk')
    @mock.patch('shaker.engine.utils.resolve_relative_path')
    def test_make_help_options_with_filter(self, resolve_mock, walk_mock):
        base_dir = 'abc/def'
        abs_dir = '/files/' + base_dir
        walk_mock.side_effect = [
            [(abs_dir + '/sub', [], ['klm.yaml']),
             (abs_dir + '/sub', [], ['ijk.html']),
             (abs_dir + '/sub', [], ['mno.yaml'])],
        ]
        resolve_mock.side_effect = [abs_dir]

        expected = 'List: "sub/klm", "sub/mno"'
        observed = utils.make_help_options(
            'List: %s', base_dir, type_filter=lambda x: x.endswith('.yaml'))
        self.assertEqual(expected, observed)

    def test_algebraic_product_empty(self):
        expected = [{}]

        observed = list(utils.algebraic_product())

        self.assertEqual(expected, observed)

    def test_algebraic_product_string(self):
        expected = [{'a': 1, 'b': 'zebra'}, {'a': 2, 'b': 'zebra'}]

        observed = list(utils.algebraic_product(a=[1, 2], b='zebra'))

        self.assertEqual(expected, observed)

    def test_algebraic_product_number(self):
        expected = [{'a': 'x', 'b': 4}, {'a': 2, 'b': 4}]

        observed = list(utils.algebraic_product(a=['x', 2], b=4))

        self.assertEqual(expected, observed)

    def test_strict(self):
        self.assertEqual('some_01_string_a',
                         utils.strict('Some 01-string (brr!) + %% A'))

    def test_set_value_by_path(self):
        data = {}
        utils.set_value_by_path(data, 'jitter.avg', 10)
        self.assertEqual({'jitter': {'avg': 10}}, data)

    def test_set_value_by_path_with_update(self):
        data = {'jitter': {'min': 5}}
        utils.set_value_by_path(data, 'jitter.avg', 10)
        self.assertEqual({'jitter': {'avg': 10, 'min': 5}}, data)

    def test_get_value_by_path(self):
        data = {'jitter': {'min': 5}}
        self.assertEqual(5, utils.get_value_by_path(data, 'jitter.min'))

    def test_get_value_by_path_none(self):
        data = {'jitter': {'min': 5}}
        self.assertIsNone(utils.get_value_by_path(data, 'jitter.avg'))

    def test_copy_value_by_path(self):
        src = {'sum': {'jitter_ms': 7}}
        dst = {}
        res = utils.copy_value_by_path(src, 'sum.jitter_ms', dst, 'jitter.avg')
        self.assertEqual({'jitter': {'avg': 7}}, dst)
        self.assertTrue(res)

    def test_copy_value_by_path_src_not_found(self):
        src = {}
        dst = {}
        res = utils.copy_value_by_path(src, 'sum.jitter_ms', dst, 'jitter.avg')
        self.assertEqual({}, dst)
        self.assertFalse(res)

    def test_merge_dicts(self):
        src = [{'a': {1: 9, 2: 8}, 'b': {1: 3}}, {'a': {3: 7}, 'c': {4: 8}}]
        expected = {'a': {1: 9, 2: 8, 3: 7}, 'b': {1: 3}, 'c': {4: 8}}
        res = utils.merge_dicts(src)
        self.assertEqual(expected, res)
