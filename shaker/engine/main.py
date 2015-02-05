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
from oslo.config import cfg
import yaml

from shaker.engine import config
from shaker.engine import heat
from shaker.engine import keystone
from shaker.engine import nova
from shaker.engine import utils
from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def run():
    keystone_kwargs = {'username': cfg.CONF.os_username,
                       'password': cfg.CONF.os_password,
                       'tenant_name': cfg.CONF.os_tenant_name,
                       'auth_url': cfg.CONF.os_auth_url,
                       }
    keystone_client = keystone.create_keystone_client(keystone_kwargs)

    heat_client = heat.create_heat_client(keystone_client)
    for stack in heat_client.stacks.list():
        LOG.info('Stacks: %s', stack)

    nova_client = nova.create_nova_client(keystone_kwargs)
    compute_nodes = [svc.host for svc in nova.get_compute_nodes(nova_client)]
    LOG.info('Compute nodes: %s', compute_nodes)

    scenario_raw = utils.read_file(cfg.CONF.scenario)

    scenario = yaml.safe_load(scenario_raw)
    LOG.info('Scenario: %s', scenario)

    mode = scenario['deployment']['mode']
    vm_count = scenario['deployment']['vm_count']
    heat_template_name = scenario['deployment']['template']
    template_parameters = scenario['deployment']['template_parameters']

    heat_template = utils.read_file(heat_template_name)

    if mode != 'pairs':
        return

    # prepare jinja template
    masters = []
    slaves = []
    for i in range(vm_count):
        masters.append(dict(name='master%s' % i, node=compute_nodes[i]))
        slaves.append(dict(name='slave%s' % i, node=compute_nodes[i]))

    vars_values = {
        'masters': masters,
        'slaves': slaves,
    }

    compiled_template = jinja2.Template(heat_template)
    rendered_template = compiled_template.render(vars_values)

    LOG.info('Rendered template: %s', rendered_template)

    template_parameters['private_net_name'] = 'net_%s' % uuid.uuid4()

    stack_name = 'shaker_%s' % uuid.uuid4()

    stack_params = {
        'stack_name': stack_name,
        'parameters': template_parameters,
        'template': rendered_template,
    }
    stack = heat_client.stacks.create(**stack_params)['stack']
    LOG.info('New stack: %s', stack)

    heat.wait_stack_completion(heat_client, stack['id'])

    outputs_list = heat_client.stacks.get(stack['id']).to_dict()['outputs']
    outputs = dict((item['output_key'], item) for item in outputs_list)

    for i in range(vm_count):
        masters[i]['public_ip'] = (outputs[masters[i]['name'] + '_public_ip']
                                   ['output_value'])
        slaves[i]['private_ip'] = (outputs[slaves[i]['name'] + '_private_ip']
                                   ['output_value'])

    LOG.info('Masters: %s', masters)
    LOG.info('Slaves: %s', slaves)

    # wait for ssh to nodes


def main():
    # init conf and logging
    conf = cfg.CONF
    conf.register_cli_opts(config.OPTS)
    conf.register_opts(config.OPTS)
    conf(project='shaker')

    logging.setup('shaker')
    LOG.info('Logging enabled')

    run()


if __name__ == '__main__':
    main()
