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

import testtools

from shaker.engine.executors import flent


IP = '10.0.0.10'
AGENT = {'slave': {'ip': IP}}


class TestFlentExecutor(testtools.TestCase):

    def test_get_command(self):
        executor = flent.FlentExecutor({}, AGENT)

        expected = {'data': (flent.FLENT_EXEC % 'flent -H %s -l 60 -s 1 '
                             'tcp_download') % IP,
                    'type': 'script'}
        self.assertEqual(expected, executor.get_command())

    def test_get_command_with_params(self):
        executor = flent.FlentExecutor(
            dict(method='ping', time=10, interval=0.5), AGENT)

        expected = {'data': (flent.FLENT_EXEC % 'flent -H %s -l 10 -s 0.5 '
                             'ping') % IP,
                    'type': 'script'}
        self.assertEqual(expected, executor.get_command())

    def test_get_command_static_host(self):
        executor = flent.FlentExecutor({'host': '10.0.0.20'}, {})

        expected = {'data': (flent.FLENT_EXEC % 'flent -H %s -l 60 -s 1 '
                             'tcp_download') % '10.0.0.20',
                    'type': 'script'}
        self.assertEqual(expected, executor.get_command())

    def test_get_expected_duration(self):
        executor = flent.FlentExecutor(dict(method='ping', time=10), AGENT)
        expected = 20
        self.assertEqual(expected, executor.get_expected_duration())

    def test_process_reply(self):
        executor = flent.FlentExecutor({}, AGENT)
        message = {
            'stdout': """
{
  "metadata": {
    "SERIES_META": {
      "Ping ICMP": {
        "UNITS": "ms"
      },
      "TCP upload": {
        "MEAN_VALUE": 14536.94,
        "UNITS": "Mbit/s"
      }
    },
    "TOTAL_LENGTH": 6
  },
  "results": {
    "Ping ICMP": [
      0.11,
      0.08003925186913663,
      0.08997269229670403,
      0.07008327936919093,
      0.07994293923635702
    ],
    "TCP upload": [
      null,
      9789.93,
      17333.075575393304,
      18173.561165616233,
      null
    ]
  },
  "x_values": [
    0.0,
    0.2,
    0.4,
    0.6000000000000001,
    0.8
  ]
}
"""
        }
        expected = {
            'samples': [
                [0.0, 0.11, None],
                [0.2, 0.08003925186913663, 9789.93],
                [0.4, 0.08997269229670403, 17333.075575393304],
                [0.6000000000000001, 0.07008327936919093, 18173.561165616233],
                [0.8, 0.07994293923635702, None]
            ],
            'meta': [
                ['time', 's'], ['ping_icmp', 'ms'], ['tcp_upload', 'Mbit/s'],
            ]
        }
        reply = executor.process_reply(message)
        self.assertEqual(expected['samples'], reply['samples'],
                         message='Samples data')
        self.assertEqual(expected['meta'], reply['meta'],
                         message='Metadata')
