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
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


HEAT_VERSION = '1'


def create_client(keystone_client, os_region_name, cacert, insecure):
    orchestration_api_url = keystone_client.service_catalog.url_for(
        service_type='orchestration', region_name=os_region_name)
    return heat_client_pkg.Client(HEAT_VERSION,
                                  endpoint=orchestration_api_url,
                                  token=keystone_client.auth_token,
                                  ca_file=cacert,
                                  insecure=insecure)


def create_stack(heat_client, stack_name, template, parameters):
    stack_params = {
        'stack_name': stack_name,
        'template': template,
        'parameters': parameters,
    }

    stack = heat_client.stacks.create(**stack_params)['stack']
    LOG.info('New stack: %s', stack)

    wait_stack_completion(heat_client, stack['id'])

    return stack['id']


def wait_stack_completion(heat_client, stack_id):
    reason = None
    status = None

    while True:
        stack = heat_client.stacks.get(stack_id)
        status = stack.status
        reason = stack.stack_status_reason
        LOG.debug('Stack status: %s', status)
        if status not in ['IN_PROGRESS', '']:
            break

        time.sleep(5)

    if status != 'COMPLETE':
        resources = heat_client.resources.list(stack_id)
        for res in resources:
            if res.resource_status != 'CREATE_COMPLETE':
                LOG.error('Heat stack resource %(res)s of type %(type)s has '
                          '%(reason)s',
                          dict(res=res.logical_resource_id,
                               type=res.resource_type,
                               reason=res.resource_status_reason))
        raise Exception('Failed to deploy Heat stack %(id)s. Expected status '
                        'COMPLETE, but got %(status)s. Reason: %(reason)s' %
                        dict(id=stack_id, status=status, reason=reason))


def get_stack_outputs(heat_client, stack_id):
    outputs_list = heat_client.stacks.get(stack_id).to_dict()['outputs']
    return dict((item['output_key'], item['output_value'])
                for item in outputs_list)
