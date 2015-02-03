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


INSTANCE_ID_URI = 'http://169.254.169.254/2009-04-04/meta-data/instance-id'


def get_instance_id():
    # return utils.read_uri(INSTANCE_ID_URI)
    return 'i-0000005f'


def poll_task(socket, instance_id):
    payload = {'operation': 'poll_task', 'instance_id': instance_id, }
    LOG.debug('Polling task: %s', payload)
    socket.send_json(payload)
    res = socket.recv_json()
    LOG.debug('Received: %s', res)
    return res


def send_result(socket, instance_id, result):
    payload = {'operation': 'send_result', 'instance_id': instance_id,
               'data': result, }
    LOG.debug('Sending result: %s', payload)
    socket.send_json(payload)
    res = socket.recv_json()
    LOG.debug('Received: %s', res)
    return res


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

    instance_id = get_instance_id()
    LOG.info('My instance id is: %s', instance_id)

    context = zmq.Context()
    LOG.info('Connecting to server: %s:%s', host, port)

    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:%s' % port)

    try:
        while True:
            task = poll_task(socket, instance_id)
            if task['operation'] == 'none':
                continue
            if task['operation'] == 'execute':
                LOG.info('Execute task: %s', task)
                # do something useful
                send_result(socket, instance_id, {'data': 'foo'})

    except BaseException as e:
        if not isinstance(e, KeyboardInterrupt):
            LOG.exception(e)
    finally:
        LOG.info('Shutting down')
        context.term()


if __name__ == "__main__":
    main()
