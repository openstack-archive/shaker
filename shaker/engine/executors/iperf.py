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

import collections
import csv

from shaker.engine.executors import base
from shaker.engine import math


class IperfExecutor(base.BaseExecutor):
    def get_command(self):
        cmd = base.CommandLine('sudo nice -n -20 iperf')
        cmd.add('--client', self.agent['slave']['ip'])
        cmd.add('--format', 'm')
        cmd.add('--nodelay')
        if self.test_definition.get('mss'):
            cmd.add('--mss', self.test_definition.get('mss'))
        cmd.add('--len', self.test_definition.get('buffer_size') or '8k')
        if self.test_definition.get('udp'):
            cmd.add('--udp')
        cmd.add('--time', self.test_definition.get('time') or 60)
        cmd.add('--parallel', self.test_definition.get('threads') or 1)
        if self.test_definition.get('csv'):
            cmd.add('--reportstyle', 'C')
        if self.test_definition.get('interval'):
            cmd.add('--interval', self.test_definition.get('interval'))
        return cmd.make()


Sample = collections.namedtuple('Sample', ['start', 'end', 'value'])


class IperfGraphExecutor(IperfExecutor):
    def get_command(self):
        self.test_definition['csv'] = True
        self.test_definition['interval'] = 1
        return super(IperfGraphExecutor, self).get_command()

    def process_reply(self, message):
        result = super(IperfGraphExecutor, self).process_reply(message)

        samples = []
        threads_count = self.test_definition.get('threads') or 1

        for row in csv.reader(result['stdout'].split('\n')):
            if row and len(row) > 8:
                thread = row[5]
                if threads_count > 1 and thread != -1:
                    # ignore individual per-thread data
                    continue

                start, end = row[6].split('-')
                samples.append(Sample(start=float(start),
                                      end=float(end),
                                      value=int(row[8])))

        samples.pop()  # the last line is summary, remove it

        result['samples'] = samples
        result.update(math.calc_traffic_stats(samples))
        return result
