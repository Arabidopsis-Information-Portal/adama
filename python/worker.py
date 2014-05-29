#!/usr/bin/env python
import argparse
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
    parser = argparse.ArgumentParser(description='A Python worker')
    parser.add_argument('--queue-host', required=True, metavar='HOST',
                        help='host where RabbitMQ is running')
    return parser.parse_args()

def main():
    hostname = parse_args().queue_host
    worker = Worker(hostname)
    print('Worker starting')
    worker.run()

if __name__ == '__main__':
    main()