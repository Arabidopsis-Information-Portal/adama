#!/usr/bin/env python

import os

from channelpy import Channel, RabbitConnection


URI = 'amqp://rabbit:5672'


def error(msg, code, ch):
    ch.put({
        'status': 'error',
        'message': msg,
        'code': code
    })


def main():
    with Channel(name='image_builder', persist=False,
                 connection_type=RabbitConnection,
                 uri=URI) as listen:
        while True:
            job = listen.get()
            with job['reply_to'] as reply_to:
                try:
                    args = job['args']
                    namespace = job['namespace']
                except KeyError:
                    error("missing 'args' and/or 'namespace': {}".format(job),
                          400, reply_to)
                    continue

                reply_to.put(
                    '[{}] will process {} and {}'
                        .format(os.getpid(), args, namespace))


if __name__ == '__main__':
    main()
