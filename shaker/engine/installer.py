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
from shaker.engine import const
from shaker.engine import utils
from shaker.openstack.clients import glance
from shaker.openstack.clients import heat
from shaker.openstack.clients import keystone
from shaker.openstack.clients import neutron
from shaker.openstack.clients import nova
from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def init():
    # init conf and logging
    conf = cfg.CONF
    conf.register_cli_opts(config.OPENSTACK_OPTS)
    conf.register_opts(config.OPENSTACK_OPTS)
    conf(project='shaker')

    logging.setup('shaker')
    LOG.info('Logging enabled')

    keystone_client = keystone.create_keystone_client(
        username=cfg.CONF.os_username, password=cfg.CONF.os_password,
        tenant_name=cfg.CONF.os_tenant_name, auth_url=cfg.CONF.os_auth_url)
    os_region_name = cfg.CONF.os_region_name or 'RegionOne'
    heat_client = heat.create_client(keystone_client, os_region_name)
    neutron_client = neutron.create_client(keystone_client, os_region_name)
    nova_client = nova.create_client(keystone_client, os_region_name)
    glance_client = glance.create_client(keystone_client, os_region_name)

    return dict(nova=nova_client, neutron=neutron_client, glance=glance_client,
                heat=heat_client)


def install():
    clients = init()

    if nova.is_flavor_exists(clients['nova'], const.SHAKER_FLAVOR_NAME):
        LOG.info('Flavor %s already exists', const.SHAKER_FLAVOR_NAME)
    else:
        clients['nova'].flavors.create(name=const.SHAKER_FLAVOR_NAME,
                                       ram=1024, vcpus=1, disk=3)
        LOG.info('Created flavor %s', const.SHAKER_FLAVOR_NAME)

    if glance.get_image(clients['glance'], const.SHAKER_IMAGE_NAME):
        LOG.info('Image %s already exists', const.SHAKER_IMAGE_NAME)
    else:
        external_net = (cfg.CONF.external_net or
                        neutron.choose_external_net(clients['neutron']))
        stack_params = {
            'stack_name': 'shaker_%s' % uuid.uuid4(),
            'parameters': {'external_net': external_net,
                           'flavor': const.SHAKER_FLAVOR_NAME},
            'template': utils.read_file('shaker/engine/installer.yaml'),
        }

        stack = clients['heat'].stacks.create(**stack_params)['stack']
        LOG.debug('New stack: %s', stack)

        heat.wait_stack_completion(clients['heat'], stack['id'])

        outputs = heat.get_stack_outputs(clients['heat'], stack['id'])
        LOG.debug('Stack outputs: %s', outputs)

        LOG.debug('Waiting for server to shutdown')
        server_id = outputs['server_info'].get('id')
        nova.wait_server_shutdown(clients['nova'], server_id)

        LOG.debug('Making snapshot')
        clients['nova'].servers.create_image(
            server_id, const.SHAKER_IMAGE_NAME)

        LOG.debug('Clearing up')
        clients['heat'].stacks.delete(stack['id'])

        LOG.info('Created image %s', const.SHAKER_IMAGE_NAME)


def uninstall():
    clients = init()

    image = glance.get_image(clients['glance'], const.SHAKER_IMAGE_NAME)
    if image:
        clients['glance'].images.delete(image)

    if nova.is_flavor_exists(clients['nova'], const.SHAKER_FLAVOR_NAME):
        clients['nova'].flavors.delete(name=const.SHAKER_FLAVOR_NAME)


if __name__ == "__main__":
    install()
