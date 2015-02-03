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
import zmq

from shaker.engine import config
from shaker.engine import utils
from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def main():
    # init conf and logging
    conf = cfg.CONF
    conf.register_cli_opts(config.AGENT_OPTS)
    conf.register_cli_opts(config.SERVER_OPTS)
    conf.register_opts(config.AGENT_OPTS)
    conf.register_opts(config.SERVER_OPTS)

    try:
        conf(project='shaker')
    except cfg.RequiredOptError as e:
        print('Error: %s' % e)
        conf.print_usage()
        exit(1)

    logging.setup('shaker')
    LOG.info('Logging enabled')

    _, agent_port = utils.split_address(cfg.CONF.agent_endpoint)
    _, server_port = utils.split_address(cfg.CONF.server_endpoint)

    agent_socket = None
    server_socket = None
    context = None

    try:
        context = zmq.Context(1)
        # Socket facing clients
        agent_socket = context.socket(zmq.XREP)
        agent_socket.bind("tcp://*:%s" % agent_port)
        LOG.info('Listen for agent connections on port: %s', agent_port)
        # Socket facing services
        server_socket = context.socket(zmq.XREQ)
        server_socket.bind("tcp://*:%s" % server_port)
        LOG.info('Listen for server connections on port: %s', server_port)

        zmq.device(zmq.QUEUE, agent_socket, server_socket)
    except BaseException as e:
        if not isinstance(e, KeyboardInterrupt):
            LOG.exception(e)
    finally:
        LOG.info('Shutting down')
        if agent_socket:
            agent_socket.close()
        if server_socket:
            server_socket.close()
        if context:
            context.term()

if __name__ == "__main__":
    main()
