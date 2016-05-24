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

from heatclient import exc
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


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


def get_stack_status(heat_client, stack_id):
    # stack.get operation may take long time and run out of time. The reason
    # is that it resolves all outputs which is done serially. On the other hand
    # stack status can be retrieved from the list operation. Internally listing
    # supports paging and every request should not take too long.
    for stack in heat_client.stacks.list():
        if stack.id == stack_id:
            return stack.status, stack.stack_status_reason
    raise exc.HTTPNotFound(message='Stack %s is not found' % stack_id)


def wait_stack_completion(heat_client, stack_id):
    reason = None
    status = None

    while True:
        status, reason = get_stack_status(heat_client, stack_id)
        LOG.debug('Stack status: %s', status)
        if status not in ['IN_PROGRESS', '']:
            break

        time.sleep(5)

    if status != 'COMPLETE':
        resources = heat_client.resources.list(stack_id)
        for res in resources:
            if (res.resource_status != 'CREATE_COMPLETE' and
                    res.resource_status_reason):
                LOG.error('Heat stack resource %(res)s of type %(type)s '
                          'failed with %(reason)s',
                          dict(res=res.logical_resource_id,
                               type=res.resource_type,
                               reason=res.resource_status_reason))
        raise Exception('Failed to deploy Heat stack %(id)s. Expected status '
                        'COMPLETE, but got %(status)s. Reason: %(reason)s' %
                        dict(id=stack_id, status=status, reason=reason))


def get_stack_outputs(heat_client, stack_id):
    # try to use optimized way to retrieve outputs, fallback otherwise
    if getattr(heat_client.stacks, 'output_list'):
        try:
            output_list = heat_client.stacks.output_list(stack_id)['outputs']

            result = {}
            for output in output_list:
                output_key = output['output_key']
                value = heat_client.stacks.output_show(stack_id, output_key)
                result[output_key] = value['output']['output_value']

            return result
        except Exception as e:
            LOG.info('Cannot get output list, fallback to old way: %s', e)

    outputs_list = heat_client.stacks.get(stack_id).to_dict()['outputs']
    return dict((item['output_key'], item['output_value'])
                for item in outputs_list)
