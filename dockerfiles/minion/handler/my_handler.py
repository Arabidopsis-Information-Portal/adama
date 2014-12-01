#!/usr/bin/env python
import json
import os

from serf_master import SerfHandler
import docker_utils
import firewall
import supervisor
from utils import truncated_stdout, with_payload, is_self


class MyHandler(SerfHandler):

    @truncated_stdout
    @with_payload
    def start(self, image=None, num_workers=None, args=None, **kwargs):
        node = kwargs.get('node', None)
        if node is not None and not is_self(node):
            return
        args = args or []
        remote_image = remote(image)
        docker_utils.docker('pull', remote_image)
        supervisor.start('worker',
                         image=remote_image,
                         numprocs=num_workers,
                         args=' '.join(args))


def remote(image):
    """Find the name of image in the registry: `LOCAL_REGISTRY`. """

    try:
        registry = os.environ['LOCAL_REGISTRY']
        return '{}/{}'.format(registry, image)
    except KeyError:
        # if LOCAL_REGISTRY is not set, default to docker hub
        return image
