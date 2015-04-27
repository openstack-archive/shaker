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

import re
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
                if svc.state == 'up' and svc.status == 'enabled']


def is_flavor_exists(nova_client, flavor_name):
    for flavor in nova_client.flavors.list():
        if flavor.to_dict()['name'] == flavor_name:
            return True
    return False


def check_server_console(nova_client, server_id, len_limit=100):
    console = nova_client.servers.get(server_id).get_console_output(len_limit)

    for line in console.splitlines():
        if (re.search(r'\[critical\]', line, flags=re.IGNORECASE) or
                re.search(r'Cloud-init.*Datasource DataSourceNone\.', line)):
            message = ('Instance %(id)s has critical cloud-init error: '
                       '%(msg)s. Check metadata service availability' %
                       dict(id=server_id, msg=line))
            LOG.error(message)
            return message
        if re.search(r'\[error', line, flags=re.IGNORECASE):
            LOG.error('Error message in instance %(id)s console: %(msg)s',
                      dict(id=server_id, msg=line))
        elif re.search(r'warn', line, flags=re.IGNORECASE):
            LOG.warn('Warn message in instance %(id)s console: %(msg)s',
                     dict(id=server_id, msg=line))

    return None


def _poll_for_status(nova_client, server_id, final_ok_states, poll_period=20,
                     status_field="status"):
    LOG.debug('Poll instance %(id)s, waiting for any of statuses %(statuses)s',
              dict(id=server_id, statuses=final_ok_states))
    while True:
        obj = nova_client.servers.get(server_id)

        err_msg = check_server_console(nova_client, server_id, len_limit=25)
        if err_msg:
            raise Exception('Critical error in instance %s console: %s' %
                            (server_id, err_msg))

        status = getattr(obj, status_field)
        if status:
            status = status.lower()

        LOG.debug('Instance %(id)s has status %(status)s',
                  dict(id=server_id, status=status))

        if status in final_ok_states:
            break
        elif status == "error" or status == 'paused':
            raise Exception(obj.fault['message'])

        time.sleep(poll_period)


def wait_server_shutdown(nova_client, server_id):
    _poll_for_status(nova_client, server_id, ['shutoff'])


def wait_server_snapshot(nova_client, server_id):
    task_state_field = "OS-EXT-STS:task_state"
    server = nova_client.servers.get(server_id)
    if hasattr(server, task_state_field):
        _poll_for_status(nova_client, server.id, [None, '-', ''],
                         status_field=task_state_field)
