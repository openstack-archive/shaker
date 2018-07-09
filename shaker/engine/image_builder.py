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

import os
import shlex
import shutil
import sys
import tempfile
import uuid

from oslo_concurrency import processutils
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
    openstack_params = utils.pack_openstack_params(cfg.CONF)
    try:
        return openstack.OpenStackClient(openstack_params)
    except Exception as e:
        LOG.error('Failed to connect to OpenStack: %s. '
                  'Please verify parameters: %s', e, openstack_params)
        exit(1)


def ensure_flavor(openstack_client, flavor_name):
    if nova.does_flavor_exist(openstack_client.nova, flavor_name):
        LOG.info('Using existing flavor: %s', flavor_name)
    else:
        try:
            nova.create_flavor(openstack_client.nova, name=flavor_name,
                               ram=cfg.CONF.flavor_ram,
                               vcpus=cfg.CONF.flavor_vcpus,
                               disk=cfg.CONF.flavor_disk)
            LOG.info('Created flavor %s', flavor_name)
        except nova.ForbiddenException:
            LOG.error('User does not have permissions to create the flavor. '
                      'Specify user with admin privileges or specify existing '
                      'flavor via --flavor-name parameter.')
            exit(1)


def build_image_with_heat(openstack_client, image_name, flavor_name,
                          dns_nameservers):
    template = None
    template_filename = cfg.CONF.image_builder_template
    try:
        am = lambda f: config.IMAGE_BUILDER_TEMPLATES + '%s.yaml' % f
        template = utils.read_file(template_filename, alias_mapper=am)
    except IOError:
        LOG.error('Error reading template file: %s. '
                  'Please verify correctness of --image-builder-template '
                  'parameter', template_filename)
        exit(1)
    external_net = (cfg.CONF.external_net or
                    neutron.choose_external_net(openstack_client.neutron))
    stack_name = 'shaker_%s' % uuid.uuid4()
    stack_parameters = {'external_net': external_net,
                        'flavor': flavor_name,
                        'dns_nameservers': dns_nameservers}
    stack_id = None
    try:
        stack_id = heat.create_stack(openstack_client.heat, stack_name,
                                     template, stack_parameters)

        outputs = heat.get_stack_outputs(openstack_client.heat, stack_id)
        LOG.debug('Stack outputs: %s', outputs)

        LOG.debug('Waiting for server to shutdown')
        server_id = outputs['server_info'].get('id')
        nova.wait_server_shutdown(openstack_client.nova, server_id)

        LOG.debug('Making snapshot')
        openstack_client.nova.servers.create_image(server_id, image_name)

        LOG.debug('Waiting for server to snapshot')
        nova.wait_server_snapshot(openstack_client.nova, server_id)

        LOG.info('Created image: %s', image_name)
    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            LOG.info('Caught SIGINT. Terminating')
        else:
            error_msg = 'Error while building the image: %s' % e
            LOG.error(error_msg)
            LOG.exception(e)
    finally:
        if stack_id and cfg.CONF.cleanup_on_error:
            LOG.debug('Cleaning up the stack: %s', stack_id)
            openstack_client.heat.stacks.delete(stack_id)


def _log_multi_line(s):
    if s:
        for line in s.split('\n'):
            if line:
                LOG.debug(line)


def build_image_with_dib(openstack_client, image_name):
    elements = utils.resolve_relative_path('shaker/resources/image_elements')
    LOG.debug('Using DIB elements from: %s', elements)

    temp_dir = None
    old_cwd = os.getcwd()

    try:
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
        filename = os.path.join(temp_dir, 'shaker-image.qcow2')
        command = 'disk-image-create -o %s %s vm shaker' % (
            filename, cfg.CONF.image_builder_distro)

        # path: local python binaries (including virtualenv) + sys.path + $PATH
        sys_path = ([sys.exec_prefix, os.path.join(sys.exec_prefix, 'bin')] +
                    sys.path + os.environ.get('PATH').split(':'))

        env = {}
        env.update(os.environ)
        env.update({'ELEMENTS_PATH': elements, 'PATH': ':'.join(sys_path)})
        if cfg.CONF.image_builder_distro == 'centos7':
            env.update({'DIB_INSTALLTYPE_pip_and_virtualenv': 'package'})

        command_stdout, command_stderr = None, None
        try:
            command_stdout, command_stderr = processutils.execute(
                *shlex.split(command), check_exit_code=True,
                root_helper='sudo', env_variables=env,
                loglevel=logging.INFO, log_errors=True)
        finally:
            _log_multi_line(command_stdout)
            _log_multi_line(command_stderr)

        LOG.info('diskimage-builder built an image %s of size %s',
                 filename, os.path.getsize(filename))

        LOG.debug('Creating image in Glance')
        image = openstack_client.glance.images.create(
            container_format='bare', disk_format='qcow2',
            name=image_name, visibility='public')

        LOG.debug('Uploading image contents into Glance')
        with open(filename, 'rb') as fd:
            openstack_client.glance.images.upload(image['id'], fd)

        LOG.info('Created image: %s', image_name)
    except Exception as e:
        LOG.error('Image build failed: %s', e)
    finally:
        if temp_dir:
            os.chdir(old_cwd)
            shutil.rmtree(temp_dir)


def ensure_image(openstack_client, image_name, flavor_name, dns_nameservers,
                 mode):
    if glance.get_image(openstack_client.glance, image_name):
        LOG.info('Using existing image: %s', image_name)
    else:
        has_v1 = (glance.get_supported_versions(openstack_client.glance) &
                  {'v1.0', 'v1.1'})

        if not has_v1 and mode == 'heat':
            LOG.warning('Glance v1.x is required to build image with Heat')

        if not mode:
            # auto-detect mode
            mode = 'heat' if has_v1 else 'dib'
            LOG.info('Detected build mode is "%s"', mode)

        if mode == 'heat':
            build_image_with_heat(openstack_client, image_name, flavor_name,
                                  dns_nameservers)
        else:
            build_image_with_dib(openstack_client, image_name)


def build_image():
    openstack_client = init()

    flavor_name = cfg.CONF.flavor_name
    image_name = cfg.CONF.image_name
    dns_nameservers = cfg.CONF.dns_nameservers
    mode = cfg.CONF.image_builder_mode

    ensure_flavor(openstack_client, flavor_name)

    ensure_image(openstack_client, image_name, flavor_name, dns_nameservers,
                 mode)


def cleanup():
    openstack_client = init()
    flavor_name = cfg.CONF.flavor_name
    image_name = cfg.CONF.image_name

    if not cfg.CONF.cleanup:
        LOG.info('Skip cleanup')
        return

    image = glance.get_image(openstack_client.glance, image_name)
    if image:
        openstack_client.glance.images.delete(image.id)

    flavor = nova.get_flavor(openstack_client.nova, flavor_name)
    if flavor:
        openstack_client.nova.flavors.delete(flavor.id)


def build_image_entry_point():
    utils.init_config_and_logging(
        config.OPENSTACK_OPTS + config.IMAGE_BUILDER_OPTS
    )
    build_image()


def cleanup_entry_point():
    utils.init_config_and_logging(config.OPENSTACK_OPTS + config.CLEANUP_OPTS)
    cleanup()


if __name__ == "__main__":
    build_image_entry_point()
