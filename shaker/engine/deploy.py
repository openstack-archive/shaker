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

from shaker.engine import const
from shaker.engine import utils
from shaker.openstack.clients import heat
from shaker.openstack.clients import keystone
from shaker.openstack.clients import neutron
from shaker.openstack.clients import nova
from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class Deployment(object):
    def __init__(self, os_username, os_password, os_tenant_name, os_auth_url,
                 os_region_name, server_endpoint, external_net):
        self.keystone_client = keystone.create_keystone_client(
            username=os_username, password=os_password,
            tenant_name=os_tenant_name, auth_url=os_auth_url)
        self.heat_client = heat.create_client(
            self.keystone_client, os_region_name)
        self.nova_client = nova.create_client(
            self.keystone_client, os_region_name)
        self.neutron_client = neutron.create_client(
            self.keystone_client, os_region_name)

        self.server_endpoint = server_endpoint
        self.external_net = (external_net or
                             neutron.choose_external_net(self.neutron_client))

        self.stack_name = 'shaker_%s' % uuid.uuid4()
        self.stack_deployed = False

    def _get_compute_nodes(self):
        return [svc.host for svc in nova.get_compute_nodes(self.nova_client)
                if svc.state == 'up']

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

    def _get_outputs(self, stack_outputs, vm_name, params):
        result = {}
        for param in params:
            o = stack_outputs.get(vm_name + '_' + param)
            if o:
                result[param] = o
        return result

    def convert_instance_name_to_agent_id(self, instance_name):
        return 'i-%s' % instance_name.split('-')[1]

    def _make_agents(self, groups, outputs):
        agents = []

        for group in groups:
            master = self._get_outputs(outputs, group['master']['name'],
                                       ['ip', 'instance_name'])
            if not master.get('instance_name'):
                LOG.info('Group is not deployed: %s. Ignoring', group)
                continue

            master.update(dict(mode='master',
                               id=self.convert_instance_name_to_agent_id(
                                   master['instance_name'])))

            slave = self._get_outputs(outputs, group['slave']['name'],
                                      ['ip', 'instance_name'])

            # todo workaround of Nova bug 1422686
            if slave.get('instance_name') and not slave.get('ip'):
                LOG.info('Ignoring group because of missing IP: %s', group)
                continue

            agents.append(master)

            if slave.get('instance_name'):
                # slave is deployed
                slave.update(dict(mode='slave',
                                  id=self.convert_instance_name_to_agent_id(
                                      slave['instance_name'])))

                master['slave_id'] = slave['id']
                slave['master_id'] = master['id']
                agents.append(slave)

        return agents

    def _deploy_from_hot(self, specification):
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
        merged_parameters = {
            'private_net_name': 'net_%s' % uuid.uuid4(),
            'private_net_cidr': '10.0.0.0/16',
            'server_endpoint': self.server_endpoint,
            'external_net': self.external_net,
            'image': const.SHAKER_IMAGE_NAME,
            'flavor': const.SHAKER_FLAVOR_NAME,
        }
        merged_parameters.update(template_parameters)

        stack_params = {
            'stack_name': self.stack_name,
            'parameters': template_parameters,
            'template': rendered_template,
        }

        stack = self.heat_client.stacks.create(**stack_params)['stack']
        LOG.info('New stack: %s', stack)

        heat.wait_stack_completion(self.heat_client, stack['id'])
        self.stack_deployed = True

        # get info about deployed objects
        outputs = heat.get_stack_outputs(self.heat_client, stack['id'])

        # convert groups into agents
        return self._make_agents(groups, outputs)

    def deploy(self, deployment):
        agents = []

        if deployment.get('template'):
            # deploy topology specified by HOT
            agents += self._deploy_from_hot(deployment)

        if deployment.get('agents'):
            # agents are specified statically
            agents += deployment.get('agents')

        return agents

    def cleanup(self):
        if self.stack_deployed:
            LOG.debug('Cleaning up the stack: %s', self.stack_name)
            self.heat_client.stacks.delete(self.stack_name)
