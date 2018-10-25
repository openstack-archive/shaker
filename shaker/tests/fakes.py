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

import uuid

DEFAULT_TIMESTAMP = '2018-10-22T00:00:00.000000'


class FakeNovaServiceList(object):
    def __init__(self, status='enabled', binary='nova-compute', zone='nova',
                 state='up', updated_at=DEFAULT_TIMESTAMP,
                 host='host-1', disabled=None):
        self.status = status
        self.binary = binary
        self.zone = zone
        self.state = state
        self.updated_at = updated_at
        self.host = host
        self.disabled = disabled
        self.id = uuid.uuid4()


class FakeNovaFlavorList(object):
    def __init__(self, name='test-flavor', ram=512, vcpus=1, disk=20,
                 extra_specs={}):
        self.name = name
        self.ram = ram
        self.vcpus = vcpus
        self.disk = disk
        self.id = uuid.uuid4()
        self.extra_specs = extra_specs

    def get_keys(self):
        return self.extra_specs


class FakeNovaAggregateList(object):
    def __init__(self, name='test-aggregate', availability_zone='nova',
                 deleted=False, created_at=DEFAULT_TIMESTAMP, updated_at='',
                 deleted_at='', hosts=[], metadata={}):
        self.name = name
        self.availability_zone = availability_zone
        self.deleted = deleted
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.hosts = hosts
        self.metadata = metadata
        self.id = uuid.uuid4()
