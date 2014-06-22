#!/usr/bin/env python
from __future__ import print_function

import argparse
import json
import logging
import os
import sys

logging.basicConfig()

import pika

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'user_code'))


class Worker(object):

    QUEUE_NAME = 'tasks'
    QUEUE_PORT = 5672

    def __init__(self, queue_host, queue_port=None, queue_name=None):
        self.queue_host = queue_host
        self.queue_port = queue_port or self.QUEUE_PORT
        self.queue_name = queue_name or self.QUEUE_NAME
        self.connect()

    def connect(self):
        """Establish a connection with the task queue."""

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.queue_host,
                                      port=self.queue_port))
        self.channel = connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback,
                                   queue=self.queue_name,
                                   no_ack=True)
        self.channel.start_consuming()

    def callback(self, channel, method, properties, body):
        reply = (channel, method, properties)
        try:
            self.process(body, reply=reply)
        except Exception as exc:
            with Results(reply):
                print(json.dumps({'error': exc.message}))
                print('END')

    def process(self, body, reply):
        import main
        metadata = json.load(open(os.path.join(HERE, 'metadata.json')))
        with Results(reply):
            d = json.loads(body)
            d['worker'] = os.uname()[1]
            body = json.dumps(d)
            main.process(json.loads(body))


class Results(object):

    def __init__(self, reply):
        self.reply = reply
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
                self.respond('\n'.join(self.lines))
                self.lines = []
            else:
                self.lines.append(line)
            if line == 'END':
                self.respond(line)
            self.current = []
        self.current.append(data)

    def respond(self, result):
        channel, method, properties = self.reply
        channel.basic_publish(exchange='',
                              routing_key=properties.reply_to,
                              body=result)




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