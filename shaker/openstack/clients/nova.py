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

import time

from novaclient import client as nova_client_pkg
from oslo_log import log as logging


LOG = logging.getLogger(__name__)

NOVA_VERSION = '2'


def create_client(keystone_session, os_region_name):
    return nova_client_pkg.Client(NOVA_VERSION, session=keystone_session,
                                  region_name=os_region_name)


def get_available_compute_nodes(nova_client):
        return [svc.host
                for svc in nova_client.services.list(binary='nova-compute')
                if svc.state == 'up']


def is_flavor_exists(nova_client, flavor_name):
    for flavor in nova_client.flavors.list():
        if flavor.to_dict()['name'] == flavor_name:
            return True
    return False


def _poll_for_status(poll_fn, obj_id, final_ok_states, poll_period=20,
                     status_field="status"):
    LOG.debug('Poll server %(id)s, waiting for any of statuses %(statuses)s',
              dict(id=obj_id, statuses=final_ok_states))
    while True:
        obj = poll_fn(obj_id)
        status = getattr(obj, status_field)
        if status:
            status = status.lower()

        LOG.debug('Server %(id)s has status %(status)s',
                  dict(id=obj_id, status=status))

        if status in final_ok_states:
            break
        elif status == "error":
            raise Exception(obj.fault['message'])

        time.sleep(poll_period)


def wait_server_shutdown(nova_client, server_id):
    _poll_for_status(nova_client.servers.get, server_id, ['shutoff'])


def wait_server_snapshot(nova_client, server_id):
    task_state_field = "OS-EXT-STS:task_state"
    server = nova_client.servers.get(server_id)
    if hasattr(server, task_state_field):
        _poll_for_status(nova_client.servers.get, server.id, [None, '-', ''],
                         status_field=task_state_field)
