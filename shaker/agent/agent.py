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
import tempfile
import time

from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log as logging
import sys
import zmq

from shaker.engine import config
from shaker.engine import utils


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


def run_command(command):
    command_stdout, command_stderr = None, None

    if command['type'] == 'program':
        command_stdout, command_stderr = processutils.execute(
            *shlex.split(command['data']), check_exit_code=False)

    elif command['type'] == 'script':
        fd = tempfile.mkstemp()
        os.write(fd[0], command['data'])
        os.close(fd[0])
        LOG.debug('stored script into %s', fd[1])
        command_stdout, command_stderr = processutils.execute(
            *shlex.split('bash %s' % fd[1]), check_exit_code=False)

    else:
        command_stderr = 'Unknown command type : %s' % command['type']

    return dict(stdout=command_stdout, stderr=command_stderr)


def main():
    utils.init_config_and_logging(config.COMMON_OPTS + config.AGENT_OPTS)

    endpoint = cfg.CONF.server_endpoint
    polling_interval = cfg.CONF.polling_interval
    agent_id = cfg.CONF.agent_id
    LOG.info('My id is: %s', agent_id)

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

                result = run_command(command)
                send_reply(socket, agent_id, result)

            elif task['operation'] == 'configure':
                if 'polling_interval' in task:
                    polling_interval = task.get('polling_interval')

            time.sleep(polling_interval)

    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            LOG.info('The process is interrupted')
            sys.exit(3)
        else:
            LOG.exception(e)

if __name__ == "__main__":
    main()
