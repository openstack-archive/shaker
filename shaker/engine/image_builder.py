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
from oslo_log import log as logging

from shaker.engine import config
from shaker.engine import utils
from shaker.openstack.clients import glance
from shaker.openstack.clients import heat
from shaker.openstack.clients import neutron
from shaker.openstack.clients import nova
from shaker.openstack.clients import openstack


LOG = logging.getLogger(__name__)


def init():
    utils.init_config_and_logging(
        config.OPENSTACK_OPTS + config.IMAGE_BUILDER_OPTS)

    openstack_client = None
    try:
        openstack_client = openstack.OpenStackClient(
            username=cfg.CONF.os_username, password=cfg.CONF.os_password,
            tenant_name=cfg.CONF.os_tenant_name, auth_url=cfg.CONF.os_auth_url,
            region_name=cfg.CONF.os_region_name)
    except Exception as e:
        LOG.error('Error establishing connection to OpenStack: %s. '
                  'Please verify OpenStack credentials (--os-username, '
                  '--os-password, --os-tenant-name, --os-auth-url)', e)
        exit(1)

    return openstack_client


def build_image():
    openstack_client = init()
    flavor_name = cfg.CONF.flavor_name
    image_name = cfg.CONF.image_name

    if nova.is_flavor_exists(openstack_client.nova, flavor_name):
        LOG.info('Using existing flavor: %s', flavor_name)
    else:
        openstack_client.nova.flavors.create(name=flavor_name,
                                             ram=512, vcpus=1, disk=3)
        LOG.info('Created flavor %s', flavor_name)

    if glance.get_image(openstack_client.glance, image_name):
        LOG.info('Using existing image: %s', image_name)
    else:
        template = None
        template_filename = cfg.CONF.image_builder_template
        try:
            template = utils.read_file(template_filename)
        except IOError:
            LOG.error('Error reading template file: %s. '
                      'Please verify correctness of --image-builder-template '
                      'parameter', template_filename)
            exit(1)

        external_net = (cfg.CONF.external_net or
                        neutron.choose_external_net(openstack_client.neutron))
        stack_params = {
            'stack_name': 'shaker_%s' % uuid.uuid4(),
            'parameters': {'external_net': external_net,
                           'flavor': flavor_name},
            'template': template,
        }

        stack = openstack_client.heat.stacks.create(**stack_params)['stack']
        LOG.debug('New stack: %s', stack)

        heat.wait_stack_completion(openstack_client.heat, stack['id'])

        outputs = heat.get_stack_outputs(openstack_client.heat, stack['id'])
        LOG.debug('Stack outputs: %s', outputs)

        LOG.debug('Waiting for server to shutdown')
        server_id = outputs['server_info'].get('id')
        nova.wait_server_shutdown(openstack_client.nova, server_id)

        LOG.debug('Making snapshot')
        openstack_client.nova.servers.create_image(
            server_id, image_name)

        LOG.debug('Waiting for server to snapshot')
        nova.wait_server_snapshot(openstack_client.nova, server_id)

        LOG.debug('Clearing up')
        openstack_client.heat.stacks.delete(stack['id'])

        LOG.info('Created image: %s', image_name)


def cleanup():
    openstack_client = init()
    flavor_name = cfg.CONF.flavor_name
    image_name = cfg.CONF.image_name

    image = glance.get_image(openstack_client.glance, image_name)
    if image:
        openstack_client.glance.images.delete(image)

    if nova.is_flavor_exists(openstack_client.nova, flavor_name):
        openstack_client.nova.flavors.delete(name=flavor_name)


if __name__ == "__main__":
    build_image()
