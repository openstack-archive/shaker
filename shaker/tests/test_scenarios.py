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

import functools
import os

import six
import testtools
import yaml

from shaker.engine import utils


class TestReport(testtools.TestCase):

    def _read_raw_file(self, file_name):
        if six.PY3:
            opener = functools.partial(open, encoding='utf8')
        else:
            opener = open
        with opener(file_name, 'r') as content_file:
            return content_file.read()

    def _iterate_files(self, root_path):
        for dir_data in os.walk(root_path):
            dir_path, dir_names, file_names = dir_data
            for file_name in file_names:
                if file_name.endswith('.yaml'):
                    yield os.path.join(dir_path, file_name)

    def test_yaml_valid(self):
        for file_name in self._iterate_files('shaker/scenarios'):
            cnt = self._read_raw_file(file_name)
            try:
                yaml.safe_load(cnt)
            except Exception as e:
                self.fail('File %s is invalid: %s' % (file_name, e))

    def test_scenario_schema_conformance(self):
        scenario_schema_file = 'shaker/resources/schemas/scenario.yaml'

        for file_name in self._iterate_files('shaker/scenarios/'):
            source_data = utils.read_yaml_file(file_name)
            schema_data = utils.read_yaml_file(scenario_schema_file)

            try:
                utils.validate_yaml(source_data, schema_data)
            except Exception as e:
                self.fail('Scenario %s does not conform to schema: %s' %
                          (file_name, e))
