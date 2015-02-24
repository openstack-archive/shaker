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
import csv
import collections
import operator

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
        LOG.debug('Test %s on agent %s finished with %s',
                  self.test_definition, self.agent, message)
        return dict(stdout=message.get('stdout'),
                    stderr=message.get('stderr'),
                    command=self.get_command(),
                    agent=self.agent)


class ShellExecutor(BaseExecutor):
    def get_command(self):
        return self.test_definition['method']


class NetperfExecutor(BaseExecutor):
    def get_command(self):
        target = self.agent['slave']['ip']
        return ('netperf -H %(target)s -l %(time)s -t %(method)s' %
                dict(target=self.test_definition.get('target') or target,
                     method=self.test_definition.get('method') or 'TCP_STREAM',
                     time=self.test_definition.get('time') or 60))


class NetperfWrapperExecutor(BaseExecutor):
    def get_command(self):
        target_ip = self.agent['slave']['ip']
        return ('netperf-wrapper -H %(ip)s -f stats %(method)s' %
                dict(ip=target_ip,
                     method=self.test_definition['method']))


class IperfExecutor(BaseExecutor):
    def get_command(self):
        target = self.agent['slave']['ip']
        mss = self.test_definition.get('mss')
        interval = self.test_definition.get('interval')
        return ('sudo nice -n -20 iperf --client %(target)s --format m'
                '%(mss)s --len %(bs)s --nodelay'
                '%(udp)s --time %(time)s --parallel %(threads)s'
                '%(css)s %(interval)s' %
                dict(target=self.test_definition.get('target') or target,
                     mss=mss and ' --mss %s' % mss or '',
                     bs=self.test_definition.get('buffer_size') or '8k',
                     udp=self.test_definition.get('udp') and ' --udp' or '',
                     threads=self.test_definition.get('threads') or 1,
                     time=self.test_definition.get('time') or 60,
                     css=self.test_definition.get('css') and ' -y C' or '',
                     interval=interval and '--interval %s' % interval or ''))


class IperfGraphExecutor(IperfExecutor):
    def get_command(self):
        self.test_definition['css'] = True
        self.test_definition['interval'] = '1'
        return super(IperfGraphExecutor, self).get_command()

    def process_reply(self, message):
        result = super(IperfGraphExecutor, self).process_reply(message)

        samples = collections.defaultdict(list)

        for row in csv.reader(result['stdout'].split('\n')):
            if row:
                thread = row[5]
                samples[thread].append(dict(
                    time=float(row[6].split('-')[1]),
                    transfer=int(row[7]),
                    bandwidth=int(row[8]),
                ))

        result['samples'] = samples

        # calc max, min, avg per thread
        bandwidth_max = collections.defaultdict(float)
        bandwidth_min = collections.defaultdict(float)
        bandwidth_avg = collections.defaultdict(float)

        for thread, data in samples.items():
            arr = [s['bandwidth'] for s in samples[thread]]
            bandwidth_max[thread] = max(arr)
            bandwidth_min[thread] = min(arr)
            bandwidth_avg[thread] = sum(arr) / len(arr)

        result['bandwidth_max'] = bandwidth_max
        result['bandwidth_min'] = bandwidth_min
        result['bandwidth_avg'] = bandwidth_avg

        return result


EXECUTORS = {
    'shell': ShellExecutor,
    'netperf': NetperfExecutor,
    'iperf': IperfExecutor,
    'iperf_graph': IperfGraphExecutor,
    'netperf_wrapper': NetperfWrapperExecutor,
    '_default': ShellExecutor,
}


def get_executor(test_definition, agent):
    # returns executor of the specified test on the specified agent
    executor_class = test_definition['class']
    klazz = EXECUTORS.get(executor_class, EXECUTORS['_default'])
    return klazz(test_definition, agent)
