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

import functools
import random

import jinja2
from oslo_config import cfg
from oslo_log import log as logging

from shaker.engine import utils
from shaker.openstack.clients import heat
from shaker.openstack.clients import neutron
from shaker.openstack.clients import nova
from shaker.openstack.clients import openstack


LOG = logging.getLogger(__name__)


def prepare_for_cross_az(compute_nodes, zones):
    if len(zones) != 2:
        LOG.warn('cross_az is specified, but len(zones) is not 2')
        return compute_nodes

    masters = []
    slaves = []
    for node in compute_nodes:
        if node['zone'] == zones[0]:
            masters.append(node)
        else:
            slaves.append(node)

    res = []
    for i in range(min(len(masters), len(slaves))):
        res.append(masters[i])
        res.append(slaves[i])

    return res


def generate_agents(compute_nodes, accommodation, unique):
    density = 1
    for s in accommodation:
        if isinstance(s, dict):
            if s.get('density'):
                density = s.get('density')
            if s.get('compute_nodes'):
                compute_nodes = random.sample(
                    compute_nodes, s.get('compute_nodes'))
            if s.get('zones'):
                compute_nodes = [c for c in compute_nodes
                                 if c['zone'] in s.get('zones')]
                if 'cross_az' in accommodation:
                    # sort nodes to interleave hosts from different zones
                    compute_nodes = prepare_for_cross_az(compute_nodes,
                                                         s.get('zones'))

    cn_count = len(compute_nodes)
    iterations = cn_count * density

    if 'single_room' in accommodation and 'pair' in accommodation:
        iterations //= 2
    node_formula = lambda x: compute_nodes[x % cn_count]

    agents = {}

    for i in range(iterations):
        if 'pair' in accommodation:
            master_id = '%s_master_%s' % (unique, i)
            slave_id = '%s_slave_%s' % (unique, i)
            master = dict(id=master_id, mode='master', slave_id=slave_id)
            slave = dict(id=slave_id, mode='slave', master_id=master_id)

            if 'single_room' in accommodation:
                master_formula = lambda x: i * 2
                slave_formula = lambda x: i * 2 + 1
            elif 'double_room' in accommodation:
                master_formula = lambda x: i
                slave_formula = lambda x: i
            else:  # mixed_room
                master_formula = lambda x: i
                slave_formula = lambda x: i + 1

            m = node_formula(master_formula(i))
            master['node'], master['zone'] = m['host'], m['zone']
            s = node_formula(slave_formula(i))
            slave['node'], slave['zone'] = s['host'], s['zone']

            agents[master['id']] = master
            agents[slave['id']] = slave
        else:
            if 'single_room' in accommodation:
                agent_id = '%s_agent_%s' % (unique, i)
                agents[agent_id] = dict(id=agent_id,
                                        node=node_formula(i)['host'],
                                        zone=node_formula(i)['zone'],
                                        mode='alone')

    if not agents:
        raise Exception('Not enough compute nodes %(cn)s for requested '
                        'instance accommodation %(acc)s' %
                        dict(cn=compute_nodes, acc=accommodation))

    return agents


def _get_stack_values(stack_outputs, vm_name, params):
    result = {}
    for param in params:
        o = stack_outputs.get(vm_name + '_' + param)
        if o:
            result[param] = o
    return result


def filter_agents(agents, stack_outputs, override=None):
    deployed_agents = {}

    # first pass, ignore non-deployed
    for agent in agents.values():
        stack_values = _get_stack_values(stack_outputs, agent['id'], ['ip'])

        if override:
            stack_values.update(override(agent))

        if not stack_values.get('ip'):
            LOG.info('Ignore non-deployed agent: %s', agent)
            continue

        agent.update(stack_values)

        # workaround of Nova bug 1422686
        if agent.get('mode') == 'slave' and not agent.get('ip'):
            LOG.info('IP address is missing in agent: %s', agent)
            continue

        deployed_agents[agent['id']] = agent

    # second pass, check pairs
    result = {}
    for agent in deployed_agents.values():
        if (agent.get('mode') == 'alone' or
                (agent.get('mode') == 'master' and
                 agent.get('slave_id') in deployed_agents) or
                (agent.get('mode') == 'slave' and
                 agent.get('master_id') in deployed_agents)):
            result[agent['id']] = agent

    return result


class Deployment(object):
    def __init__(self, server_endpoint):
        self.server_endpoint = server_endpoint
        self.openstack_client = None
        self.stack_created = False

    def connect_to_openstack(self, os_username, os_password, os_tenant_name,
                             os_auth_url, os_region_name, external_net,
                             flavor_name, image_name, os_cacert, os_insecure):
        LOG.debug('Connecting to OpenStack')

        self.openstack_client = openstack.OpenStackClient(
            username=os_username, password=os_password,
            tenant_name=os_tenant_name, auth_url=os_auth_url,
            region_name=os_region_name, cacert=os_cacert, insecure=os_insecure)

        self.flavor_name = flavor_name
        self.image_name = image_name
        self.external_net = (external_net or
                             neutron.choose_external_net(
                                 self.openstack_client.neutron))
        self.stack_name = 'shaker_%s' % utils.random_string()

    def _deploy_from_hot(self, specification, base_dir=None):
        agents = generate_agents(
            nova.get_available_compute_nodes(self.openstack_client.nova),
            specification.get('accommodation') or
            specification.get('vm_accommodation'),
            self.stack_name)

        # render template by jinja
        vars_values = {
            'agents': agents,
            'unique': self.stack_name,
        }
        heat_template = utils.read_file(specification['template'],
                                        base_dir=base_dir)
        compiled_template = jinja2.Template(heat_template)
        rendered_template = compiled_template.render(vars_values)
        LOG.debug('Rendered template: %s', rendered_template)

        # create stack by Heat
        merged_parameters = {
            'server_endpoint': self.server_endpoint,
            'external_net': self.external_net,
            'image': self.image_name,
            'flavor': self.flavor_name,
        }
        merged_parameters.update(specification.get('template_parameters', {}))

        stack_id = heat.create_stack(
            self.openstack_client.heat, self.stack_name, rendered_template,
            merged_parameters)
        self.stack_created = True

        # get info about deployed objects
        outputs = heat.get_stack_outputs(self.openstack_client.heat, stack_id)
        override = self._get_override(specification.get('override'))

        return filter_agents(agents, outputs, override)

    def _get_override(self, override_spec):
        def override_ip(agent, ip_type):
            return dict(ip=nova.get_server_ip(
                self.openstack_client.nova, agent['id'], ip_type))

        if override_spec:
            if override_spec.get('ip'):
                return functools.partial(override_ip,
                                         ip_type=override_spec.get('ip'))

    def deploy(self, deployment, base_dir=None):
        agents = {}

        if deployment.get('template'):
            if not self.openstack_client:
                LOG.error('OpenStack client is not initialized. Template '
                          'deployment is ignored.')
            else:
                # deploy topology specified by HOT
                agents.update(self._deploy_from_hot(
                    deployment, base_dir=base_dir))

        if deployment.get('agents'):
            # agents are specified statically
            agents.update(dict((a['id'], a) for a in deployment.get('agents')))

        return agents

    def cleanup(self):
        if self.stack_created and cfg.CONF.cleanup_on_error:
            LOG.debug('Cleaning up the stack: %s', self.stack_name)
            self.openstack_client.heat.stacks.delete(self.stack_name)
        else:
            LOG.info('No Heat Stack clean-up as no cleanup on error'
                     'requested or static agents were deployed')
