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

from neutronclient.neutron import client as neutron_client_pkg

from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


NEUTRON_VERSION = '2.0'


def create_client(keystone_client, os_region_name):
    network_api_url = keystone_client.service_catalog.url_for(
        service_type='network', region_name=os_region_name)
    return neutron_client_pkg.Client(NEUTRON_VERSION,
                                     endpoint_url=network_api_url,
                                     token=keystone_client.auth_token)


def choose_external_net(neutron_client):
    ext_nets = neutron_client.list_networks(
        **{'router:external': True})['networks']
    if not ext_nets:
        raise Exception('No external networks found')
    return ext_nets[0]['name']
