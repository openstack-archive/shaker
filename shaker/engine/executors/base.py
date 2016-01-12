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
        if param_value is not None:
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

    def get_expected_duration(self):
        """Get the expected duration of executor's run
        The value is used by Quorum to calculate expected time of reply.
        :return: time in seconds
        """
        return self.test_definition.get('time') or 60

    def get_command(self):
        return None

    def process_reply(self, message):
        LOG.debug('Test %s on agent %s finished with %s',
                  self.test_definition, self.agent, message)
        return dict(stdout=message.get('stdout'),
                    stderr=message.get('stderr'),
                    start=message.get('start'),
                    finish=message.get('finish'),
                    command=self.get_command())

    def process_failure(self):
        return dict(command=self.get_command())


class ExecutorException(Exception):
    def __init__(self, record, message):
        super(ExecutorException, self).__init__(message)
        self.record = record
