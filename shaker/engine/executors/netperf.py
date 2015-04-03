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

from shaker.engine.executors import base


class NetperfExecutor(base.BaseExecutor):
    def get_command(self):
        cmd = base.CommandLine('netperf')
        cmd.add('-H', self.agent['slave']['ip'])
        cmd.add('-l', self.get_test_duration())
        cmd.add('-t', self.test_definition.get('method') or 'TCP_STREAM')
        return cmd.make()


class NetperfWrapperExecutor(base.BaseExecutor):
    def get_command(self):
        cmd = base.CommandLine('netperf-wrapper')
        cmd.add('-H', self.agent['slave']['ip'])
        cmd.add('-l', self.get_test_duration())
        cmd.add('-s', self.test_definition.get('interval') or 1)
        cmd.add('-f', 'csv')
        cmd.add(self.test_definition.get('method') or 'tcp_download')
        return cmd.make()

    def process_reply(self, message):
        result = super(NetperfWrapperExecutor, self).process_reply(message)

        data_stream = csv.reader(result['stdout'].split('\n'))

        header = next(data_stream)
        meta = [['time', 's']]
        for el in header[1:]:
            if el.find('Ping') >= 0:
                meta.append([el, 'ms'])
            else:
                meta.append([el, 'Mbps'])
        result['meta'] = meta

        result['samples'] = [[(float(x) if x else None) for x in row]
                             for row in data_stream if row]
        return result
