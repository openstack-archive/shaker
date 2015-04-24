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

import multiprocessing
import time

from oslo_log import log as logging

from shaker.agent import agent as agent_process
from shaker.engine import messaging


LOG = logging.getLogger(__name__)


class BaseOperation(object):
    def get_agent_join_timeout(self):
        return 0

    def get_active_agent_ids(self):
        pass

    def get_reply(self, agent_id, start_at):
        return {}

    def process_reply(self, agent_id, message):
        return {'status': 'ok'}

    def process_failure(self, agent_id):
        return {'status': 'lost'}

    def process_interrupt(self, agent_id):
        return {'status': 'interrupted'}


class JoinOperation(BaseOperation):
    def __init__(self, agent_ids, polling_interval, agent_join_timeout):
        super(JoinOperation, self).__init__()
        self.agent_ids = agent_ids
        self.polling_interval = polling_interval
        self.agent_join_timeout = agent_join_timeout

    def get_agent_join_timeout(self):
        return self.agent_join_timeout

    def get_active_agent_ids(self):
        return set(self.agent_ids)

    def get_reply(self, agent_id, start_at):
        return dict(operation='configure',
                    polling_interval=self.polling_interval,
                    expected_duration=0)


class ExecuteOperation(BaseOperation):
    def __init__(self, executors):
        super(ExecuteOperation, self).__init__()
        self.executors = executors

    def get_active_agent_ids(self):
        return set(self.executors.keys())

    def get_reply(self, agent_id, start_at):
        reply = dict(operation='execute',
                     start_at=start_at,
                     command=self.executors[agent_id].get_command(),
                     expected_duration=(self.executors[agent_id].
                                        get_expected_duration()))
        return reply

    def process_reply(self, agent_id, message):
        r = super(ExecuteOperation, self).process_reply(agent_id, message)
        r.update(self.executors[agent_id].process_reply(message))
        return r

    def process_failure(self, agent_id):
        r = super(ExecuteOperation, self).process_failure(agent_id)
        r.update(self.executors[agent_id].process_failure())
        return r

    def process_interrupt(self, agent_id):
        r = super(ExecuteOperation, self).process_interrupt(agent_id)
        r.update(self.executors[agent_id].process_failure())
        return r


class Quorum(object):
    def __init__(self, message_queue, polling_interval, agent_loss_timeout,
                 agent_join_timeout):
        self.message_queue = message_queue
        self.polling_interval = polling_interval
        self.agent_loss_timeout = agent_loss_timeout
        self.agent_join_timeout = agent_join_timeout

    def _run(self, operation):
        current = operation.get_active_agent_ids()
        LOG.debug('Executing operation %s on agents: %s', operation, current)

        working = set()
        replied = set()
        result = {}

        start_at = time.time() + self.polling_interval * 2
        lives = dict((agent_id, start_at + operation.get_agent_join_timeout())
                     for agent_id in current)

        for message, reply_handler in self.message_queue:
            agent_id = message.get('agent_id')
            op = message.get('operation')
            reply = {'operation': 'none'}
            now = time.time()

            if agent_id in (current - replied):
                # message from a known not yet worked agent
                lives[agent_id] = (now + self.polling_interval * 2 +
                                   self.agent_loss_timeout)

                if op == 'poll':
                    reply = operation.get_reply(agent_id, start_at)
                    lives[agent_id] += reply.get('expected_duration')
                    working.add(agent_id)
                    LOG.debug('Working agents: %s', working)
                elif op == 'reply':
                    if agent_id in working:
                        result[agent_id] = operation.process_reply(
                            agent_id, message)
                        replied.add(agent_id)
                        LOG.debug('Replied agents: %s', replied)

            reply_handler(reply)

            lost = set(a for a, t in lives.items() if t < now) - replied
            if lost:
                LOG.debug('Lost agents: %s', lost)

            if replied | lost >= current:
                if lost:
                    LOG.warning('Lost agents: %s', lost)
                    # update result with info about lost agents
                    for agent_id in lost:
                        result[agent_id] = operation.process_failure(agent_id)

                LOG.info('Finished processing operation: %s', operation)
                break

        # treat missing agents as interrupted
        interrupted = current - set(result.keys())
        if interrupted:
            LOG.info('Interrupted agents: %s', interrupted)
            result.update(dict((a_id, operation.process_interrupt(a_id))
                          for a_id in interrupted))

        # update records with scheduling time
        for record in result.values():
            record['schedule'] = start_at

        return result

    def join(self, agent_ids):
        LOG.debug('Waiting for quorum of agents: %s', agent_ids)
        return self._run(JoinOperation(agent_ids, self.polling_interval,
                                       self.agent_join_timeout))

    def execute(self, executors):
        return self._run(ExecuteOperation(executors))


def make_quorum(agent_ids, server_endpoint, polling_interval,
                agent_loss_timeout, agent_join_timeout):
    message_queue = messaging.MessageQueue(server_endpoint)

    heartbeat = multiprocessing.Process(
        target=agent_process.work,
        kwargs=dict(agent_id='heartbeat', endpoint=server_endpoint,
                    polling_interval=polling_interval))
    heartbeat.daemon = True
    heartbeat.start()

    quorum = Quorum(message_queue, polling_interval, agent_loss_timeout,
                    agent_join_timeout)
    quorum.join(set(agent_ids))
    return quorum
