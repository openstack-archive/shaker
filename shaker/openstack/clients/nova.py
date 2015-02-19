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

from novaclient import client as nova_client_pkg


NOVA_VERSION = '2'


def create_nova_client(keystone_client, os_region_name):
    compute_api_url = keystone_client.service_catalog.url_for(
        service_type='compute', region_name=os_region_name)
    client = nova_client_pkg.Client(NOVA_VERSION,
                                    auth_token=keystone_client.auth_token)
    client.set_management_url(compute_api_url)
    return client


def get_compute_nodes(nova_client):
    return nova_client.services.list(binary='nova-compute')
