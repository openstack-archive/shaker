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

from oslo_log import log as logging

from shaker.engine.executors import base


LOG = logging.getLogger(__name__)


class ShellExecutor(base.BaseExecutor):
    def get_command(self):
        if 'program' in self.test_definition:
            cmd = base.CommandLine(self.test_definition['program'])
        elif 'script' in self.test_definition:
            cmd = base.Script(self.test_definition['script'])
        return cmd.make()
