#!/usr/bin/env python
import pika
import sys


class MyClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='127.0.0.1'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='my', durable=True)
        self.result = self.channel.queue_declare(exclusive=True)
        self.result_queue = self.result.method.queue
        self.channel.basic_consume(self.on_response,
                                   queue=self.result_queue,
                                   no_ack=True)

    def on_response(self, ch, method, props, body):
        self.response = body

    def call(self, msg):
        self.response = None
        self.channel.basic_publish(exchange='',
                                   routing_key='my',
                                   body=msg,
                                   properties=pika.BasicProperties(
                                       # make message persistent
                                       delivery_mode=2,
                                       reply_to=self.result_queue))
        print " [x] Sent %r" % (msg,)
        while self.response is None:
            self.connection.process_data_events()
        return self.response


if __name__ == '__main__':
    client = MyClient()
    print(client.call(sys.argv[1]))