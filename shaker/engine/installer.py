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

from oslo_config import cfg

from shaker.engine import config
from shaker.engine import utils
from shaker.openstack.clients import glance
from shaker.openstack.clients import heat
from shaker.openstack.clients import keystone
from shaker.openstack.clients import neutron
from shaker.openstack.clients import nova
from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)

SHAKER_FLAVOR_NAME = 'shaker-flavor'
SHAKER_IMAGE_NAME = 'shaker-image-x'


def install_image(os_username, os_password, os_tenant_name, os_auth_url,
                  os_region_name, external_net):
    keystone_client = keystone.create_keystone_client(
        username=os_username, password=os_password,
        tenant_name=os_tenant_name, auth_url=os_auth_url)
    heat_client = heat.create_client(keystone_client, os_region_name)
    neutron_client = neutron.create_client(keystone_client, os_region_name)
    nova_client = nova.create_client(keystone_client, os_region_name)
    glance_client = glance.create_client(keystone_client, os_region_name)

    if not nova.is_flavor_exists(nova_client, SHAKER_FLAVOR_NAME):
        nova_client.flavors.create(name=SHAKER_FLAVOR_NAME, ram=1024,
                                   vcpus=1, disk=3)
        LOG.info('Created flavor %s', SHAKER_FLAVOR_NAME)
    else:
        LOG.info('Flavor %s already exists', SHAKER_FLAVOR_NAME)

    if not glance.is_image_exists(glance_client, SHAKER_IMAGE_NAME):
        external_net = (external_net or
                        neutron.choose_external_net(neutron_client))
        stack_params = {
            'stack_name': 'shaker_%s' % uuid.uuid4(),
            'parameters': {'external_net': external_net,
                           'flavor': SHAKER_FLAVOR_NAME},
            'template': utils.read_file('shaker/engine/installer.yaml'),
        }

        stack = heat_client.stacks.create(**stack_params)['stack']
        LOG.debug('New stack: %s', stack)

        heat.wait_stack_completion(heat_client, stack['id'])

        outputs = heat.get_stack_outputs(heat_client, stack['id'])
        LOG.debug('Stack outputs: %s', outputs)

        LOG.debug('Waiting for server to shutdown')
        server_id = outputs['server_info'].get('id')
        nova.wait_server_shutdown(nova_client, server_id)

        LOG.debug('Making snapshot')
        nova_client.servers.create_image(server_id, SHAKER_IMAGE_NAME)

        LOG.debug('Clearing up')
        heat_client.stacks.delete(stack['id'])

        LOG.info('Created image %s', SHAKER_IMAGE_NAME)


def main():
    # init conf and logging
    conf = cfg.CONF
    conf.register_cli_opts(config.OPENSTACK_OPTS)
    conf.register_opts(config.OPENSTACK_OPTS)
    conf(project='shaker')

    logging.setup('shaker')
    LOG.info('Logging enabled')

    install_image(cfg.CONF.os_username, cfg.CONF.os_password,
                  cfg.CONF.os_tenant_name, cfg.CONF.os_auth_url,
                  cfg.CONF.os_region_name or 'RegionOne',
                  cfg.CONF.external_net)


if __name__ == "__main__":
    main()
