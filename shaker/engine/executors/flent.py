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

import json

from shaker.engine.executors import base
from shaker.engine import utils


FLENT_EXEC = 'zcat `%s 2>&1 | grep "se with" | grep -Po \'\\./\\S+\'`'
FLENT_EXTRA_TIME = 10  # by default flent adds by 5 secs before and after run


class FlentExecutor(base.BaseExecutor):
    def get_command(self):
        cmd = base.CommandLine('flent')
        cmd.add('-H', self.test_definition.get('host') or
                self.agent['slave']['ip'])
        cmd.add('-l', self.test_definition.get('time') or 60)
        cmd.add('-s', self.test_definition.get('interval') or 1)
        cmd.add(self.test_definition.get('method') or 'tcp_download')
        flent_cmd = cmd.make()
        return base.Script(FLENT_EXEC % flent_cmd['data']).make()

    def get_expected_duration(self):
        return (super(FlentExecutor, self).get_expected_duration() +
                FLENT_EXTRA_TIME)

    def process_reply(self, message):
        result = super(FlentExecutor, self).process_reply(message)

        stdout = result['stdout']
        if not stdout:
            raise base.ExecutorException(
                result,
                'Flent returned no data, stderr: %s' % result['stderr'])

        data = json.loads(stdout)

        series_meta = data['metadata']['SERIES_META']
        columns = sorted(series_meta.keys())
        meta = ([['time', 's']] +
                [[utils.strict(k), series_meta[k]['UNITS']] for k in columns])
        samples = []

        for i in range(len(data['x_values'])):
            line = [data['x_values'][i]]
            for el in columns:
                line.append(data['results'][el][i])
            samples.append(line)

        result['meta'] = meta
        result['samples'] = samples

        return result
