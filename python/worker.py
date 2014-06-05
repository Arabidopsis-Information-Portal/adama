#!/usr/bin/env python
import logging
logging.basicConfig()

import argparse
import json
import os

import pika

import sys
here_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here_dir, 'user_code'))


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
        self.channel.basic_consume(self.callback, queue=self.queue_name)
        self.channel.start_consuming()

    @staticmethod
    def callback(channel, method, properties, body):
        print('Received:', body)
        try:
            result = self.process(body)
        except Exception as exc:
            result = {'error': exc.message}
        channel.basic_publish(exchange='',
                              routing_key=properties.reply_to,
                              body=json.dumps(result))
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def process(self, body):
        import main
        metadata = json.load(open('metadata.json'))
        result = main.process(json.loads(body))
        return result


def parse_args():
    parser = argparse.ArgumentParser(description='A Python worker',
                                     epilog='--*--')
    parser.add_argument('--queue-host', metavar='HOST',
                        help='host where RabbitMQ is running')
    parser.add_argument('--queue-port', metavar='PORT',
                        type=int, default=5672,
                        help='port where RabbitMQ is running')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='run interactive console')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.interactive:
        os.execlp('ipython', 'ipython')
    worker = Worker(args.queue_host, args.queue_port)
    print('Worker starting')
    worker.run()


if __name__ == '__main__':
    main()