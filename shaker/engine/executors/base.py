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


LOG = logging.getLogger(__name__)


class CommandLine(object):
    def __init__(self, command):
        self.tokens = [command]

    def add(self, param_name, param_value=None):
        self.tokens.append('%s' % param_name)
        if param_value:
            self.tokens.append(str(param_value))

    def make(self):
        return dict(type='program', data=' '.join(self.tokens))


class Script(object):
    def __init__(self, script):
        self.script = script

    def make(self):
        return dict(type='script', data=self.script)


class BaseExecutor(object):
    def __init__(self, test_definition, agent):
        super(BaseExecutor, self).__init__()
        self.test_definition = test_definition
        self.agent = agent

    def get_command(self):
        return None

    def process_reply(self, message):
        LOG.debug('Test %s on agent %s finished with %s',
                  self.test_definition, self.agent, message)
        return dict(stdout=message.get('stdout'),
                    stderr=message.get('stderr'),
                    command=self.get_command(),
                    agent=self.agent)
