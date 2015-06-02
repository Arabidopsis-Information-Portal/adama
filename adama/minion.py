#!/usr/bin/env python
from __future__ import print_function

import json
import time
import os
import sys

from tasks import QueueConnection, SimpleProducer


class Minion(QueueConnection):
    """A server to create workers.

    Format of the message::

        "image": str
        "numprocs": int,
        "args": List[str]  (extra args for "docker run -d image ...")

    """

    def callback(self, message, responder):
        print('Got {}'.format(message))
        time.sleep(10)
        responder(json.dumps({'ok': True}))

    def run(self):
        print("Starting minion server with queue {}:{} "
              "and channel 'minion_server'"
              .format(self.queue_host, self.queue_port),
              file=sys.stderr)
        self.consume_forever(self.callback)


def main():
    host, port = os.environ['RABBITMQ_SERVER'].split(':')
    minion = Minion(host, int(port), 'minion_server')
    minion.run()


def client():
    host, port = os.environ['RABBITMQ_SERVER'].split(':')
    return SimpleProducer(host, int(port), 'minion_server')


if __name__ == '__main__':
    main()