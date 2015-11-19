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

from shaker.engine.executors import flent
from shaker.engine.executors import iperf
from shaker.engine.executors import netperf
from shaker.engine.executors import shell


EXECUTORS = {
    'shell': shell.ShellExecutor,
    'netperf': netperf.NetperfExecutor,
    'iperf': iperf.IperfExecutor,
    'iperf_graph': iperf.IperfGraphExecutor,
    'iperf3': iperf.Iperf3Executor,
    'flent': flent.FlentExecutor,
    '_default': shell.ShellExecutor,
}


def get_executor(test_definition, agent):
    # returns executor of the specified test on the specified agent
    executor_class = test_definition['class']
    klazz = EXECUTORS.get(executor_class, EXECUTORS['_default'])
    return klazz(test_definition, agent)
