import json

import pika


class Client(object):

    QUEUE_NAME = 'tasks'
    QUEUE_PORT = 5672

    def __init__(self, queue_host, queue_port=None, queue_name=None):
        self.queue_host = queue_host
        self.queue_port = queue_port or self.QUEUE_PORT
        self.queue_name = queue_name or self.QUEUE_NAME
        self.connect()

    def connect(self):
        """Establish a connection with the task queue."""

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.queue_host,
                                      port=self.queue_port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def send(self, message):
        """Send a message to the queue.

        Return immediately. Use `receive` to get the result.

        """
        serialized_msg = json.dumps(message)
        self.result = self.channel.queue_declare(exclusive=True)
        self.result_queue = self.result.method.queue
        self.channel.basic_consume(self.on_response,
                                   queue=self.result_queue,
                                   no_ack=True)
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=serialized_msg,
                                   properties=pika.BasicProperties(
                                       # make message persistent
                                       delivery_mode=2,
                                       reply_to=self.result_queue))
        print("Sent:", message)

    def receive(self):
        """Receive a result from the queue.

        It will block if there is no result yet.

        """
        self.done = False
        self.response = []
        while not self.done:
            self.connection.process_data_events()
        return self.response

    def on_response(self, ch, method, props, body):
        if body == 'END':
            self.done = True
        else:
            self.response.append(json.loads(body))
