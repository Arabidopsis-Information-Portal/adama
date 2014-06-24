#!/usr/bin/env python
from __future__ import print_function

import argparse
import json
import logging
import os
import sys

from tasks import QueueConnection

logging.basicConfig()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'user_code'))


class Worker(QueueConnection):

    def callback(self, message, responder):
        with Results(responder):
            try:
                self.process(message)
            except Exception as exc:
                print(json.dumps({'error': exc.message}))
                print('END')

    def process(self, body):
        import main
        metadata = json.load(open(os.path.join(HERE, 'metadata.json')))
        d = json.loads(body)
        d['worker'] = os.uname()[1]
        body = json.dumps(d)
        main.process(json.loads(body))

    def run(self):
        self.consume_forever(self.callback)


class Results(object):

    def __init__(self, responder):
        self.responder = responder
        self.current = []
        self.lines = []

    def __enter__(self):
        self.old_stdout = sys.stdout
        self.old_stdout.flush()
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.old_stdout

    def write(self, data):
        if '\n' in data:
            old, data = data.split('\n', 1)
            self.current.append(old)
            line = ' '.join(self.current).strip()
            if line == '---' or (line == 'END' and self.lines):
                self.responder('\n'.join(self.lines))
                self.lines = []
            else:
                self.lines.append(line)
            if line == 'END':
                self.responder(line)
            self.current = []
        self.current.append(data)


def parse_args():
    parser = argparse.ArgumentParser(description='A Python worker',
                                     epilog='--*--')
    parser.add_argument('--queue-host', metavar='HOST',
                        help='host where RabbitMQ is running')
    parser.add_argument('--queue-port', metavar='PORT',
                        type=int, default=5672,
                        help='port where RabbitMQ is running')
    parser.add_argument('--queue-name', metavar='NAME',
                        help='name of the queue this worker will use',
                        default=None)
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='run interactive console')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.interactive:
        os.execlp('ipython', 'ipython')
    worker = Worker(args.queue_host, args.queue_port, args.queue_name)
    print('Worker v0.1.5 starting', file=sys.stderr)
    print('Listening in queue {}'.format(args.queue_name), file=sys.stderr)
    print('*** WORKER STARTED', file=sys.stderr)
    worker.run()
    # If worker stops consuming, it's because of an error
    print('*** WORKER ERROR', file=sys.stderr)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('*** WORKER ERROR', file=sys.stderr)
        raise