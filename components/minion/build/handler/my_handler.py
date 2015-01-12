#!/usr/bin/env python
import json
import os

from base_handler import BaseHandler
import docker_utils
import firewall
import supervisor
from utils import truncated_stdout, with_payload
from serf import is_self, where


class MyHandler(BaseHandler):

    @truncated_stdout
    @with_payload
    def start(self, image=None, num_workers=None, args=None, **kwargs):
        node = kwargs.get('node', None)
        if node is not None and not is_self(node):
            return
        args = args or []
        print('going to pull', image)
        #remote_image = remote(image)
        remote_image = image
        docker_utils.docker('pull', remote_image)
        supervisor.start('worker.conf',
                         target='worker_{}'.format(image),
                         image=remote_image,
                         numprocs=num_workers,
                         args=' '.join(args))

    @truncated_stdout
    @with_payload
    def check(self, image=None, num_workers=None, **kwargs):
        pass


def remote(image):
    """Find the name of image in the registry: `LOCAL_REGISTRY`. """

    try:
        registry = list(where('registry'))[0]
        return '{}/{}'.format(registry, image)
    except IndexError:
        # if LOCAL_REGISTRY is not set, default to docker hub
        return image
