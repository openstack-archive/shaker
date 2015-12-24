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


class TestReport(testtools.TestCase):

    def _read_raw_file(self, file_name):
        if six.PY3:
            opener = functools.partial(open, encoding='utf8')
        else:
            opener = open
        with opener(file_name, 'r') as content_file:
            return content_file.read()

    def test_yaml_valid(self):
        for dir_data in os.walk('shaker/scenarios'):
            dir_path, dir_names, file_names = dir_data
            for file_name in file_names:
                if not file_name.endswith('.yaml'):
                    continue

                cnt = self._read_raw_file(os.path.join(dir_path, file_name))
                try:
                    yaml.safe_load(cnt)
                except Exception as e:
                    self.fail('File %s is invalid: %s' % (file_name, e))
