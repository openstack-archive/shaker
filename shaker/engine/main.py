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

from oslo.config import cfg

from shaker.engine import config
from shaker.engine import heat
from shaker.engine import keystone
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
