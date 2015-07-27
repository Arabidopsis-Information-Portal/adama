#!/usr/bin/env python

import os
import uuid
import threading
from traceback import format_exc

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


def start_registration(guid, args, namespace):
    """
    :type guid: str
    :type args: Dict
    :type namespace: str
    """
    REGISTRATION_STORE[guid] = {
        'status': 'starting'
    }
    try:
        service = do_register(args, namespace)
        REGISTRATION_STORE[guid] = {
            'status': 'success',
            'service': service.iden
        }
        # notify success
    except Exception as exc:
        REGISTRATION_STORE[guid] = {
            'status': 'failed',
            'message': str(exc),
            'traceback': format_exc()
        }
        # notify failure


def do_register(args, namespace):
    """
    :type args: Dict
    :type namespace: str
    :rtype: Service
    """
    if 'code' in args or args.get('type') == 'passthrough':
        service = register_code(args, namespace)
    elif 'git_repository' in args:
        service = register_git_repository(args, namespace)
    else:
        raise APIException('no code or git repository specified')
    return service


def main():
    with Channel(name='image_builder', persist=False,
                 connection_type=RabbitConnection,
                 uri=RABBIT_URI) as listen:
        while True:
            job = listen.get()
            t = threading.Thread(target=process, args=(job,))
            t.start()


def process(job):
    """
    :type job: Dict
    """
    with job['reply_to'] as reply_to:
        try:
            args = job['value']['args']
            namespace = job['value']['namespace']
        except KeyError:
            error("missing 'args' and/or 'namespace': {}".format(job),
                  400, reply_to)
            return

        guid = uuid.uuid4().hex
        reply_to.put({
            'message': guid,
            'status': 'ok'
        })
        start_registration(guid, args, namespace)


if __name__ == '__main__':
    main()
