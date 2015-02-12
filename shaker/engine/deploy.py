# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid

import jinja2

from shaker.engine import heat
from shaker.engine import keystone
from shaker.engine import nova
from shaker.engine import utils
from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class Deployment(object):
    def __init__(self, os_username, os_password, os_tenant_name, os_auth_url,
                 server_endpoint):
        self.server_endpoint = server_endpoint
        keystone_kwargs = {'username': os_username,
                           'password': os_password,
                           'tenant_name': os_tenant_name,
                           'auth_url': os_auth_url,
                           }
        self.keystone_client = keystone.create_keystone_client(keystone_kwargs)
        self.heat_client = heat.create_heat_client(self.keystone_client)
        self.nova_client = nova.create_nova_client(keystone_kwargs)

        self.stack_name = 'shaker_%s' % uuid.uuid4()

    def _get_compute_nodes(self):
        return [svc.host for svc in nova.get_compute_nodes(self.nova_client)]

    def _make_groups(self, vm_accommodation):
        compute_nodes = self._get_compute_nodes()
        cn_count = len(compute_nodes)
        iterations = cn_count
        if 'single_room' in vm_accommodation and 'pair' in vm_accommodation:
            iterations /= 2
        node_formulae = lambda x: compute_nodes[x % cn_count]

        groups = []

        for i in range(iterations):
            group = dict(master=dict(name='master_%s' % i),
                         slave=dict(name='slave_%s' % i))

            if 'pair' in vm_accommodation:
                if 'single_room' in vm_accommodation:
                    group['master']['node'] = node_formulae(i * 2)
                    group['slave']['node'] = node_formulae(i * 2 + 1)
                elif 'double_room' in vm_accommodation:
                    group['master']['node'] = node_formulae(i)
                    group['slave']['node'] = node_formulae(i)
                elif 'mixed_room' in vm_accommodation:
                    group['master']['node'] = node_formulae(i)
                    group['slave']['node'] = node_formulae(i + 1)
            else:
                if 'single_room' in vm_accommodation:
                    group['master']['node'] = node_formulae(i)
            groups.append(group)

        return groups

    def _get_output(self, vm, stack_outputs, vm_name, param):
        o = stack_outputs.get(vm_name + '_' + param)
        if o:
            vm[param] = o['output_value']

    def _copy_vm_attributes(self, vm, stack_outputs, attributes):
        for attribute in attributes:
            self._get_output(vm, stack_outputs, vm['name'], attribute)

    def deploy(self, specification):
        vm_accommodation = specification['vm_accommodation']
        heat_template_name = specification['template']
        template_parameters = specification['template_parameters']
        heat_template = utils.read_file(heat_template_name)
        groups = self._make_groups(vm_accommodation)

        # render template by jinja
        vars_values = {
            'groups': groups,
        }
        compiled_template = jinja2.Template(heat_template)
        rendered_template = compiled_template.render(vars_values)
        LOG.debug('Rendered template: %s', rendered_template)

        # create stack by Heat
        template_parameters['private_net_name'] = 'net_%s' % uuid.uuid4()
        template_parameters['server_endpoint'] = self.server_endpoint

        stack_params = {
            'stack_name': self.stack_name,
            'parameters': template_parameters,
            'template': rendered_template,
        }

        stack = self.heat_client.stacks.create(**stack_params)['stack']
        LOG.info('New stack: %s', stack)

        heat.wait_stack_completion(self.heat_client, stack['id'])

        # get info about deployed objects
        outputs_list = self.heat_client.stacks.get(
            stack['id']).to_dict()['outputs']
        outputs = dict((item['output_key'], item) for item in outputs_list)

        for group in groups:
            self._copy_vm_attributes(group['master'], outputs,
                                     ['ip', 'instance_name'])
            self._copy_vm_attributes(group['slave'], outputs,
                                     ['ip', 'instance_name'])

        LOG.debug('Groups: %s', groups)
        return groups

    def cleanup(self):
        LOG.debug('Cleaning up the stack: %s', self.stack_name)
        self.heat_client.stacks.delete(self.stack_name)
