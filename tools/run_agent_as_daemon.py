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

# This is a helper script for integration testing that runs agent as daemon

import argparse
import os
import signal
import sys

from daemonize import Daemonize

from shaker.agent import agent


def stop_daemon(pid_file_name):
    try:
        with open(pid_file_name) as fd:
            pid = fd.read()
    except IOError:
        return

    try:
        os.kill(int(pid), signal.SIGKILL)
    except Exception:
        pass

    try:
        os.remove(pid_file_name)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description='Shaker agent')
    parser.add_argument('--start',
                        action='store_true',
                        help='Start the daemon')
    parser.add_argument('--stop',
                        action='store_true',
                        help='Stop the daemon')
    parser.add_argument('--pid',
                        help='Name of file where PID is stored')
    args = parser.parse_args()

    def start():
        sys.argv = sys.argv[:1]
        agent.main()

    pid_file_name = args.pid

    if args.start:
        if os.path.exists(pid_file_name):
            stop_daemon(pid_file_name)
        daemon = Daemonize(app="shaker-agent", pid=pid_file_name, action=start)
        daemon.start()
    elif args.stop:
        stop_daemon(pid_file_name)
    else:
        start()


if __name__ == '__main__':
    main()
