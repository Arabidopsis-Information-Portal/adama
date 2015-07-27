#!/usr/bin/env python

import os
import uuid

from channelpy import Channel, RabbitConnection

from store import Store


REGISTRATION_STORE = Store(
    host=os.environ.get('REDIS_PORT_6379_TCP_ADDR', '172.17.42.1'),
    port=int(os.environ.get('REDIS_PORT_6379_TCP_PORT', 6379)),
    db=9
)
RABBIT_URI = 'amqp://{}:{}'.format(
    os.environ.get('RABBIT_PORT_5672_TCP_ADDR', '172.17.42.1'),
    os.environ.get('RABBIT_PORT_5672_TCP_PORT', 5672)
)


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
    REGISTRATION_STORE[guid] = {
        'status': 'starting'
    }
    spawn()


def spawn():
    pass


def main():
    with Channel(name='image_builder', persist=False,
                 connection_type=RabbitConnection,
                 uri=RABBIT_URI) as listen:
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
