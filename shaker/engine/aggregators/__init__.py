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

from shaker.engine.aggregators import base
from shaker.engine.aggregators import traffic


AGGREGATORS = {
    'iperf_graph': traffic.TrafficAggregator,
    'iperf3': traffic.TrafficAggregator,
    'flent': traffic.TrafficAggregator,
    '_default': base.BaseAggregator,
}


def get_aggregator(test_definition):
    # returns executor of the specified test on the specified agent
    executor_class = test_definition['class']
    klazz = AGGREGATORS.get(executor_class, AGGREGATORS['_default'])
    return klazz(test_definition)
