import argparse
import os
import signal
import sys

from daemonize import Daemonize

from shaker.agent import agent

PID_FILE = '/tmp/shaker-agent.pid'


def stop_daemon():
    try:
        with open(PID_FILE) as fd:
            pid = fd.read()
    except IOError:
        return

    try:
        os.kill(int(pid), signal.SIGKILL)
    except Exception:
        pass

    try:
        os.remove(PID_FILE)
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
    args = parser.parse_args()

    def start():
        sys.argv = sys.argv[:1]
        agent.main()

    if args.start:
        if os.path.exists(PID_FILE):
            stop_daemon()
        daemon = Daemonize(app="shaker-agent", pid=PID_FILE, action=start)
        daemon.start()
    elif args.stop:
        stop_daemon()
    else:
        start()


if __name__ == '__main__':
    main()
