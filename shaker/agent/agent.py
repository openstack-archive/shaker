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

import shlex
import time

from oslo_concurrency import processutils
from oslo_config import cfg
import zmq

from shaker.engine import config
from shaker.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def poll_task(socket, agent_id):
    payload = {
        'operation': 'poll',
        'agent_id': agent_id,
    }
    LOG.debug('Polling task: %s', payload)
    socket.send_json(payload)
    res = socket.recv_json()
    LOG.debug('Received: %s', res)
    return res


def send_reply(socket, agent_id, result):
    message = {
        'operation': 'reply',
        'agent_id': agent_id,
    }
    message.update(result)

    LOG.debug('Sending reply: %s', message)
    socket.send_json(message)
    res = socket.recv_json()
    LOG.debug('Received: %s', res)
    return res


def main():
    # init conf and logging
    conf = cfg.CONF
    conf.register_cli_opts(config.COMMON_OPTS)
    conf.register_cli_opts(config.AGENT_OPTS)
    conf.register_opts(config.COMMON_OPTS)
    conf.register_opts(config.AGENT_OPTS)

    try:
        conf(project='shaker')
    except cfg.RequiredOptError as e:
        print('Error: %s' % e)
        conf.print_usage()
        exit(1)

    logging.setup('shaker')
    LOG.info('Logging enabled')

    endpoint = cfg.CONF.server_endpoint

    agent_id = cfg.CONF.agent_id
    LOG.info('My instance id is: %s', agent_id)

    context = zmq.Context()
    LOG.info('Connecting to server: %s', endpoint)

    socket = context.socket(zmq.REQ)
    socket.connect('tcp://%s' % endpoint)

    try:
        while True:
            task = poll_task(socket, agent_id)

            if task['operation'] == 'execute':
                now = int(time.time())
                start_at = task.get('start_at') or now
                command = task.get('command')
                LOG.debug('Scheduling command %s at %s', command, start_at)

                time.sleep(start_at - now)

                # do something useful
                command_stdout, command_stderr = processutils.execute(
                    *shlex.split(command))
                send_reply(socket, agent_id, {
                    'stdout': command_stdout,
                    'stderr': command_stderr,
                })

            time.sleep(10)

    except BaseException as e:
        if not isinstance(e, KeyboardInterrupt):
            LOG.exception(e)
    finally:
        LOG.info('Shutting down')


if __name__ == "__main__":
    main()
