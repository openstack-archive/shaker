# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from shaker.openstack.clients import glance
from shaker.openstack.clients import heat
from shaker.openstack.clients import keystone
from shaker.openstack.clients import neutron
from shaker.openstack.clients import nova


CLIENT_MAKERS = {
    'glance': glance.create_client,
    'heat': heat.create_client,
    'neutron': neutron.create_client,
    'nova': nova.create_client,
}


class OpenStackClient(object):
    def __init__(self, username, password, tenant_name, auth_url, region_name):
        super(OpenStackClient, self).__init__()

        self.keystone_client = keystone.create_keystone_client(
            username=username, password=password, tenant_name=tenant_name,
            auth_url=auth_url)
        self.region_name = region_name or 'RegionOne'

    def __getattribute__(self, name):
        if name in CLIENT_MAKERS:
            return CLIENT_MAKERS[name](self.keystone_client, self.region_name)
        else:
            return super(OpenStackClient, self).__getattribute__(name)
