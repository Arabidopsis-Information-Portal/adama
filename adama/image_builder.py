#!/usr/bin/env python

import os
import uuid

from channelpy import Channel, RabbitConnection

from adama.stores import registration_store


URI = 'amqp://rabbit:5672'


def error(msg, code, ch):
    """
    :type msg: Any
    :type code: int
    :type ch: Channel
    """
    ch.put({
        'status': 'error',
        'message': msg,
        'code': code
    })


def handle(guid, args, namespace):
    """
    :type guid: str
    :type args: Dict
    :type namespace: str
    """
    registration_store[guid] = {
        'status': 'starting'
    }
    spawn()


def main():
    with Channel(name='image_builder', persist=False,
                 connection_type=RabbitConnection,
                 uri=URI) as listen:
        while True:
            job = listen.get()
            with job['reply_to'] as reply_to:
                try:
                    args = job['value']['args']
                    namespace = job['value']['namespace']
                except KeyError:
                    error("missing 'args' and/or 'namespace': {}".format(job),
                          400, reply_to)
                    continue

                guid = uuid.uuid4().hex
                handle(guid, args, namespace)

                reply_to.put({
                    'message': guid,
                    'status': 'ok'
                })


if __name__ == '__main__':
    main()
