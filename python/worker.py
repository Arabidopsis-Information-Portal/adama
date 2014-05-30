#!/usr/bin/env python
import logging
logging.basicConfig()

import argparse
import os
import sys
import time

import pika


class Worker(object):

    QUEUE_NAME = 'tasks'

    def __init__(self, queue_host, queue_name=None):
        self.queue_host = queue_host
        self.queue_name = queue_name or self.QUEUE_NAME
        self.connect()

    def connect(self):
        """Establish a connection with the task queue."""

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.queue_host))
        self.channel = connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue=self.queue_name)
        self.channel.start_consuming()

    @staticmethod
    def callback(channel, method, properties, body):
        print('Received:', body)
        channel.basic_publish(exchange='',
                              routing_key=properties.reply_to,
                              body=body)
        channel.basic_ack(delivery_tag=method.delivery_tag)


def parse_args():
    parser = argparse.ArgumentParser(description='A Python worker',
                                     epilog='--*--')
    parser.add_argument('--queue-host', metavar='HOST',
                        help='host where RabbitMQ is running')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='run interactive console')
    return parser.parse_args()

def main():
    args = parse_args()
    if args.interactive:
        os.execlp('ipython', 'ipython')
    worker = Worker(args.queue_host)
    print('Worker starting')
    worker.run()

if __name__ == '__main__':
    main()