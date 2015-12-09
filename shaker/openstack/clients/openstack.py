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

import functools
import time

from shaker.openstack.clients import glance
from shaker.openstack.clients import heat
from shaker.openstack.clients import keystone
from shaker.openstack.clients import neutron
from shaker.openstack.clients import nova


# As of now only Nova and Neutron clients support Keystone sessions.
# Thus the only way to create clients is from keystone client instance
# and auth token. The token gets expired in an hour and there is no
# way to automatically refresh it. So the current implementation is to
# recreate keystone client from scratch

MODERN_CLIENT_MAKERS = {
    'neutron': neutron.create_client,
    'nova': nova.create_client,
}
OLD_CLIENT_MAKERS = {
    'glance': glance.create_client,
    'heat': heat.create_client,
}

KEYSTONE_AUTH_EXPIRATION = 60


class OpenStackClientProxy(object):
    def __init__(self, keystone_creator, client_creator):
        self.keystone_creator = keystone_creator
        self.client_creator = client_creator
        self.last_update_time = 0

    def __getattribute__(self, name):
        if name in ['keystone_creator', 'client_creator',
                    'client', 'last_update_time']:
            return super(OpenStackClientProxy, self).__getattribute__(name)
        else:
            now = int(time.time())
            if now > self.last_update_time + KEYSTONE_AUTH_EXPIRATION:
                self.last_update_time = now
                self.client = self.client_creator(
                    keystone_client=self.keystone_creator())
            return self.client.__getattribute__(name)


class OpenStackClient(object):
    def __init__(self, username, password, tenant_name, auth_url, region_name,
                 cacert, insecure):
        self.region_name = region_name or 'RegionOne'
        self.cacert = cacert or ''
        self.insecure = insecure or False
        self._osc_cache = {}
        self.keystone_creator = functools.partial(
            keystone.create_keystone_client,
            username=username, password=password,
            tenant_name=tenant_name, auth_url=auth_url, cacert=cacert,
            insecure=insecure)
        self.session_creator = functools.partial(
            keystone.create_keystone_session, cacert,
            username=username, password=password,
            tenant_name=tenant_name, auth_url=auth_url,
            insecure=insecure)
        # ping OpenStack
        self.keystone_creator()

    def __getattribute__(self, name):
        if name != '_osc_cache' and name in self._osc_cache:
            return self._osc_cache[name]

        client = None
        if name in MODERN_CLIENT_MAKERS:
            session = self.session_creator()
            client = MODERN_CLIENT_MAKERS[name](session, self.region_name)
        elif name in OLD_CLIENT_MAKERS:
            client_creator = functools.partial(
                OLD_CLIENT_MAKERS[name], os_region_name=self.region_name,
                cacert=self.cacert, insecure=self.insecure)
            client = OpenStackClientProxy(self.keystone_creator,
                                          client_creator)

        if client:
            self._osc_cache[name] = client
            return client
        else:
            return super(OpenStackClient, self).__getattribute__(name)
