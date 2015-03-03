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


def mean(array):
    if not array:
        return 0
    return sum(array) / len(array)


def calc_traffic_stats(samples):
    total = sum(sample.value for sample in samples)
    duration = sum((sample.end - sample.start) for sample in samples)

    values = [int(sample.value / (sample.end - sample.start))
              for sample in samples]
    row_data = [[sample.end, sample.value / (sample.end - sample.start)]
                for sample in samples]

    return dict(
        stats=dict(
            max=max(values),
            min=min(values),
            mean=mean(values),
            total=total,
            duration=duration,
        ),
        row_data=row_data,
    )
