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

from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient import client as nova_client_pkg


def create_nova_client(keystone_client):
    auth = v2.Password(**keystone_client)
    sess = session.Session(auth=auth)
    return nova_client_pkg.Client('2', session=sess)


def get_compute_nodes(nova_client):
    return nova_client.services.list(binary='nova-compute')
