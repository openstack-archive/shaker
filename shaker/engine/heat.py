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

from heatclient import client as heat_client_pkg

from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


HEAT_CLIENT_VERSION = '1'


def create_heat_client(keystone_client):
    orchestration_api_url = keystone_client.service_catalog.url_for(
        service_type='orchestration')
    client = heat_client_pkg.Client(HEAT_CLIENT_VERSION,
                                    endpoint=orchestration_api_url,
                                    token=keystone_client.auth_token, )
    return client


def wait_stack_completion(heat_client, stack_id):
    status = None

    while True:
        status = heat_client.stacks.get(stack_id).status
        LOG.debug('Stack status: %s', status)
        if status not in ['IN_PROGRESS', '']:
            break

        time.sleep(1)

    if status != 'COMPLETE':
        raise Exception(status)
