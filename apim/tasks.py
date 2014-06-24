from __future__ import print_function

from functools import partial
import json
import sys
from textwrap import dedent

import pika


class AbstractQueueConnection(object):
    """A task queue.

    Implement this interface to provide a task queue for the
    workers.

    """

    def connect(self):
        """Establish the connection."""
        pass

    def send(self, message):
        """Send an asynchronous message."""
        pass

    def receive(self):
        """Return multiple responses.

        It should be a generator that produces each response.  The
        user is supposed to send `True` back to the generator when all
        the responses are returned.

        """
        pass

    def consume_forever(self, callback):
        """Consume and invoke `callback`.

        `callback` has the signature::

            f(message, responder)

        where `responder` is a function with signature::

            g(message)

        that can be used to answer to the producer.

        """
        pass

    def delete(self):
        """Delete this queue."""
        pass


class QueueConnection(AbstractQueueConnection):

    def __init__(self, queue_host, queue_port, queue_name):
        self.queue_host = queue_host
        self.queue_port = queue_port
        self.queue_name = queue_name
        self.connect()

    def delete(self):
        self.channel.queue_delete(self.queue_name)

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
        self.response = None
        self.result = self.channel.queue_declare(exclusive=True)
        self.result_queue = self.result.method.queue
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=message,
                                   properties=pika.BasicProperties(
                                       # make message persistent
                                       delivery_mode=2,
                                       reply_to=self.result_queue))

    def receive(self):
        """Receive results from the queue.

        A generator returning objects from the queue. It will block if
        there are no objects yet.

        The end of the stream is marked by sending `True` back to the
        generator.

        """
        while True:
            (ok, props, message) = self.channel.basic_get(
                self.result_queue, no_ack=True)
            if ok is not None:
                is_done = yield message
                if is_done:
                    return

    def consume_forever(self, callback):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(partial(self.on_consume, callback),
                                   queue=self.queue_name,
                                   no_ack=True)
        self.channel.start_consuming()

    def on_consume(self, callback, ch, method, props, body):

        def responder(result):
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             body=result)

        callback(body, responder)


class Producer(QueueConnection):
    """Send messages to the queue exchange and receive answers.

    The `receive` method behaves as a generator, returning a stream of
    messages.

    """

    def send(self, message):
        super(Producer, self).send(json.dumps(message))

    def receive(self):
        """Receive messages until getting `END`."""

        g = super(Producer, self).receive()
        for message in g:
            if message == 'END':
                g.send(True)
                return
            yield json.loads(message)


def check_queue(display=False):
    """Check that we can establish a connection to the queue."""

    from apim.config import Config

    host = Config.get('queue', 'host')
    port = Config.getint('queue', 'port')
    try:
        q = QueueConnection(queue_host=host,
                            queue_port=port,
                            queue_name='test')
        q.delete()
        return True
    except Exception:
        if display:
            print(dedent(
                """
                Cannot connect to queue exchange at {0}:{1}
                with dummy queue "test".
                Please, check ~/.apim.conf
                """.format(host, port)), file=sys.stderr)
        raise
        return False
