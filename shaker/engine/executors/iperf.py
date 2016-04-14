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
import json
import yaml

from shaker.engine.executors import base
from shaker.engine import utils


def add_common_iperf_params(cmd, executor):
    cmd.add('--client', executor.test_definition.get('host') or
            executor.agent['slave']['ip'])
    cmd.add('--format', 'm')
    if executor.test_definition.get('mss'):
        cmd.add('--mss', executor.test_definition.get('mss'))
    if executor.test_definition.get('buffer_size'):
        cmd.add('--len', executor.test_definition.get('buffer_size'))
    if executor.test_definition.get('udp'):
        cmd.add('--udp')
        if executor.test_definition.get('bandwidth') is not None:
            cmd.add('--bandwidth', executor.test_definition.get('bandwidth'))
        if executor.test_definition.get('datagram_size'):
            cmd.add('--len', executor.test_definition.get('datagram_size'))
    cmd.add('--time', executor.get_expected_duration())
    cmd.add('--parallel', executor.test_definition.get('threads') or 1)
    if executor.test_definition.get('interval'):
        cmd.add('--interval', executor.test_definition.get('interval'))


class IperfExecutor(base.BaseExecutor):
    def get_command(self):
        cmd = base.CommandLine('iperf')
        add_common_iperf_params(cmd, self)
        cmd.add('--nodelay')
        if self.test_definition.get('csv'):
            cmd.add('--reportstyle', 'C')
        return cmd.make()


class IperfGraphExecutor(IperfExecutor):
    def get_command(self):
        self.test_definition['csv'] = True
        self.test_definition['interval'] = 1
        return super(IperfGraphExecutor, self).get_command()

    def process_reply(self, message):
        result = super(IperfGraphExecutor, self).process_reply(message)

        if not result['stdout']:
            raise base.ExecutorException(result, 'Empty result from iperf')

        samples = []
        threads_count = self.test_definition.get('threads') or 1

        for row in csv.reader(result['stdout'].split('\n')):
            if row and len(row) > 8:
                thread = row[5]
                if threads_count > 1 and thread != '-1':
                    # ignore individual per-thread data
                    continue

                start, end = row[6].split('-')
                samples.append([float(end), int(row[8])])

        if samples:
            samples.pop()  # the last line is summary, remove it

        result['samples'] = samples
        result['meta'] = [['time', 's'], ['bandwidth', 'bit/s']]
        return result


class Iperf3Executor(base.BaseExecutor):
    def get_command(self):
        if not self.test_definition.get('interval'):
            self.test_definition['interval'] = 1

        cmd = base.CommandLine('iperf3')
        add_common_iperf_params(cmd, self)
        cmd.add('--json')
        if self.test_definition.get('reverse'):
            cmd.add('--reverse')
        return cmd.make()

    def process_reply(self, message):
        result = super(Iperf3Executor, self).process_reply(message)

        if not result['stdout']:
            raise base.ExecutorException(result, 'Empty result from iperf')

        data = json.loads(result['stdout'])

        # store verbose data in result
        result['verbose'] = yaml.safe_dump(
            dict(start=data['start'], end=data['end']),
            indent=2, default_flow_style=False)

        if 'error' in data:
            raise base.ExecutorException(result, data['error'])

        has_retransmits = False
        if (len(data['intervals']) > 0 and
                'retransmits' in data['intervals'][0]['sum']):
            has_retransmits = True

        if self.test_definition.get('udp'):
            sampler = lambda p: [round(p['end'], 2), p['packets']]
            meta = [['time', 's'], ['packets', 'pps']]
        elif has_retransmits:
            sampler = lambda p: [round(p['end'], 2), p['bits_per_second'],
                                 p['retransmits']]
            meta = [['time', 's'], ['bandwidth', 'bit/s'], ['retransmits', '']]
        else:
            sampler = lambda p: [round(p['end'], 2), p['bits_per_second']]
            meta = [['time', 's'], ['bandwidth', 'bit/s']]

        samples = []
        for point in data['intervals']:
            samples.append(sampler(point['sum']))

        result['samples'] = samples
        result['meta'] = meta

        stats = result['stats'] = {}
        if utils.copy_value_by_path(data, 'end.sum.jitter_ms',
                                    stats, 'jitter.avg'):
            utils.set_value_by_path(stats, 'jitter.unit', 'ms')

        if utils.copy_value_by_path(data, 'end.sum.lost_percent',
                                    stats, 'loss.avg'):
            utils.set_value_by_path(stats, 'loss.unit', '%')

        return result
