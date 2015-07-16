#!/usr/bin/env python

import os

from channelpy import Channel


URI = 'amqp://rabbit:5672'


def error(msg, ch):
    ch.put(
        {
        }
    )


def main():
    with Channel(name='image_builder', uri=URI, persist=True) as listen:
        while True:
            job = listen.get()

            try:
                reply_to = job['reply_to']
                assert isinstance(reply_to, Channel)
            except (KeyError, AssertionError):
                print("invalid or missing 'reply_to': {}".format(job))
                continue

            try:
                args = job['args']
                namespace = job['namespace']
            except KeyError:
                error("missing 'args' and/or 'namespace': {}".format(job),
                      reply_to)
                continue

            reply_to.put(
                '[{}] will process {} and {}'
                    .format(os.getpid(), args, namespace))


if __name__ == '__main__':
    main()
