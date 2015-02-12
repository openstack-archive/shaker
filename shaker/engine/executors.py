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

from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class BaseExecutor(object):
    def __init__(self, test_definition, agent):
        super(BaseExecutor, self).__init__()
        self.test_definition = test_definition
        self.agent = agent

    def get_command(self):
        return None

    def process_reply(self, message):
        pass


class ShellExecutor(BaseExecutor):
    def get_command(self):
        return self.test_definition['method']

    def process_reply(self, message):
        LOG.debug('Test %s on agent %s finished with %s',
                  self.test_definition, self.agent, message)


class NetperfExecutor(BaseExecutor):
    def get_command(self):
        target_ip = self.agent['group']['slave']['ip']
        return ('netperf -H %(ip)s -l 30 -t %(method)s' %
                dict(ip=target_ip,
                     method=self.test_definition['method']))

    def process_reply(self, message):
        LOG.debug('Test %s on agent %s finished with %s',
                  self.test_definition, self.agent, message)


class NetperfWrapperExecutor(BaseExecutor):
    def get_command(self):
        target_ip = self.agent['group']['slave']['ip']
        return ('netperf-wrapper -H %(ip)s -f stats %(method)s' %
                dict(ip=target_ip,
                     method=self.test_definition['method']))

    def process_reply(self, message):
        LOG.debug('Test %s on agent %s finished with %s',
                  self.test_definition, self.agent, message)


EXECUTORS = {
    'shell': ShellExecutor,
    'netperf': NetperfExecutor,
    'netperf_wrapper': NetperfWrapperExecutor,
    '_default': ShellExecutor,
}


def get_executor(test_definition, agent):
    # returns executor of the specified test on the specified agent
    executor_class = test_definition['class']
    klazz = EXECUTORS.get(executor_class, EXECUTORS['_default'])
    return klazz(test_definition, agent)
