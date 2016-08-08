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

import time
import traceback

from oslo_log import log as logging

from shaker.agent import agent as agent_process
from shaker.engine.executors import base as base_executors


LOG = logging.getLogger(__name__)

HEARTBEAT_AGENT = '__heartbeat'
CLEANER_AGENT = '__cleaner'


class BaseOperation(object):
    def get_agent_join_timeout(self):
        return 0

    def get_active_agent_ids(self):
        pass

    def get_default_reply(self, agent_id):
        return {'operation': 'none'}

    def get_reply(self, agent_id, start_at):
        return {}

    def process_reply(self, agent_id, message):
        return {'status': 'ok'}

    def process_error(self, agent_id, exception):
        return {'status': 'error', 'info': str(exception),
                'traceback': traceback.format_exc()}

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
        try:
            reply = self.executors[agent_id].process_reply(message)
            r = super(ExecuteOperation, self).process_reply(agent_id, message)
            r.update(reply)
        except base_executors.ExecutorException as e:
            LOG.error('Error while processing reply: %s', e)
            r = super(ExecuteOperation, self).process_error(agent_id, e)
            r.update(e.record)
        except Exception as e:
            LOG.error('Error while processing reply: %s', e)
            r = super(ExecuteOperation, self).process_error(agent_id, e)

        return r

    def process_failure(self, agent_id):
        r = super(ExecuteOperation, self).process_failure(agent_id)
        r.update(self.executors[agent_id].process_failure())
        return r

    def process_interrupt(self, agent_id):
        r = super(ExecuteOperation, self).process_interrupt(agent_id)
        r.update(self.executors[agent_id].process_failure())
        return r


class CleanOperation(BaseOperation):
    def __init__(self, polling_interval):
        self.polling_interval = polling_interval

    def get_active_agent_ids(self):
        return {CLEANER_AGENT}

    def get_default_reply(self, agent_id):
        reply = super(CleanOperation, self).get_default_reply(agent_id)
        if agent_id != HEARTBEAT_AGENT:
            # send all agents sleep
            reply['start_at'] = time.time() + self.polling_interval * 4
        return reply


class Quorum(object):
    def __init__(self, message_queue, polling_interval, agent_loss_timeout,
                 agent_join_timeout):
        self.message_queue = message_queue
        self.polling_interval = polling_interval
        self.agent_loss_timeout = agent_loss_timeout
        self.agent_join_timeout = agent_join_timeout

    def __del__(self):
        LOG.info('Cleaning the quorum')
        self._run(CleanOperation(self.polling_interval))

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
            reply = operation.get_default_reply(agent_id)
            now = time.time()

            if agent_id in (current - replied):
                # message from a known not yet worked agent
                lives[agent_id] = (now + self.polling_interval * 2 +
                                   self.agent_loss_timeout)
                op = message.get('operation')

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
                    filtered = set(a for a in lost if a[0] != '_')
                    if filtered:  # do not warn about private agents
                        LOG.warning('Lost agents: %s', filtered)
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
        LOG.info('Waiting for quorum of agents: %s', agent_ids)
        return self._run(JoinOperation(agent_ids, self.polling_interval,
                                       self.agent_join_timeout))

    def execute(self, executors):
        return self._run(ExecuteOperation(executors))


class LocalQuorum(object):
    def execute(self, executors):
        operation = ExecuteOperation(executors)
        agent_ids = operation.get_active_agent_ids()
        result = {}

        for agent_id in agent_ids:
            task = operation.get_reply(agent_id, None)
            command_res = agent_process.run_command(task.get('command'))
            result[agent_id] = operation.process_reply(agent_id, command_res)

        return result


def make_quorum(agent_ids, message_queue, polling_interval,
                agent_loss_timeout, agent_join_timeout):
    quorum = Quorum(message_queue, polling_interval, agent_loss_timeout,
                    agent_join_timeout)
    result = quorum.join(set(agent_ids))

    failed = dict((agent_id, rec['status'])
                  for agent_id, rec in result.items() if rec['status'] != 'ok')
    if failed:
        raise Exception('Agents failed to join: %s' % failed)

    return quorum


def make_local_quorum():
    return LocalQuorum()
