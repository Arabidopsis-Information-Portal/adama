#!/usr/bin/env python
from __future__ import print_function

import argparse
import json
import importlib
import logging
import os
import sys
import time
import traceback

from tasks import QueueConnection

logging.basicConfig()

HERE = os.path.dirname(os.path.abspath(__file__))


class QueryWorker(QueueConnection):

    def callback(self, message, responder):
        t = None
        with Results(responder):
            try:
                t = self.operation(message)
            except Exception as exc:
                print(json.dumps({
                    'error': exc.message,
                    'traceback': traceback.format_exc()
                }))
            finally:
                print('END')
                responder(json.dumps({'time_in_main': t}))

    def operation(self, body):
        d = json.loads(body)
        d['worker'] = os.uname()[1]
        endpoint = d['endpoint']
        body = json.dumps(d)
        t_start = time.time()

        getattr(self.module, endpoint)(json.loads(body))

        t_end = time.time()
        return t_end - t_start

    def run(self):
        main_module_path = os.environ.get('MAIN_MODULE_PATH', '')
        main_module_name = os.environ['MAIN_MODULE_NAME']
        module_name, _ = os.path.splitext(main_module_name)
        sys.path.insert(0, os.path.join(HERE, 'user_code', main_module_path))
        self.module = importlib.import_module(module_name)

        self.consume_forever(self.callback)


class ProcessWorker(QueueConnection):

    def run(self):
        main_module_path = os.environ.get('MAIN_MODULE_PATH', '')
        main_module_name = os.environ['MAIN_MODULE_NAME']
        module_name, _ = os.path.splitext(main_module_name)
        sys.path.insert(0, os.path.join(HERE, 'user_code', main_module_path))
        self.module = importlib.import_module(module_name)

        self.consume_forever(self.callback)

    def callback(self, message, responder):
        try:
            out = self.module.process(json.loads(message))
            if out is not None:
                responder(json.dumps(out))
        except Exception as exc:
            responder(json.dumps({
                'error': exc.message,
                'traceback': traceback.format_exc()
            }))
        finally:
            responder('END')
            responder(json.dumps({}))


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
    parser.add_argument('--adapter-type', metavar='KIND',
                        help='type of the adapter: "process" or "query"',
                        default=None)
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='run interactive console')
    return parser.parse_args()


def get_class_for(kind):
    """Map the type of adapter to the proper class."""

    map = {
        'map': ProcessWorker,
        'query': QueryWorker
    }
    return map[kind]


def run_worker(worker_type, args):
    worker_class = get_class_for(worker_type)
    worker = worker_class(
        args.queue_host, args.queue_port, args.queue_name)
    print('Worker of type {} v0.1.5 starting'.format(worker_type),
          file=sys.stderr)
    print('Listening in queue {}'.format(args.queue_name),
          file=sys.stderr)
    print('*** WORKER STARTED', file=sys.stderr)
    try:
        worker.run()
    finally:
        traceback.print_exc(file=sys.stderr)
        # If worker stops consuming, it's because of an error
        print('*** WORKER ERROR', file=sys.stderr)


def main():
    args = parse_args()
    if args.interactive:
        os.execlp('ipython', 'ipython')
    run_worker(args.adapter_type, args)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('*** WORKER ERROR', file=sys.stderr)
        raise