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

import random

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
    conf.register_opts(config.AGENT_OPTS)

    try:
        conf(project='shaker')
    except cfg.RequiredOptError as e:
        print('Error: %s' % e)
        conf.print_usage()
        exit(1)

    logging.setup('shaker')
    LOG.info('Logging enabled')

    host, port = utils.split_address(cfg.CONF.agent_endpoint)

    context = zmq.Context()
    LOG.info('Connecting to server: %s:%s', host, port)

    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:%s' % port)
    client_id = random.randrange(1, 10005)

    # Do 10 requests, waiting each time for a response
    try:
        for request in range(10):
            LOG.debug('Sending request %s' % request)
            socket.send('Hello from %s' % client_id)
            #  Get the reply.
            message = socket.recv()
            LOG.debug('Received reply %s [%s]', request, message)
    except BaseException as e:
        if not isinstance(e, KeyboardInterrupt):
            LOG.exception(e)
    finally:
        LOG.info('Shutting down')
        context.term()


if __name__ == "__main__":
    main()
