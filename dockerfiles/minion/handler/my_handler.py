#!/usr/bin/env python
import json
import os

from serf_master import SerfHandler
import docker_utils
import firewall
from utils import truncated_stdout, with_payload


class MyHandler(SerfHandler):

    @truncated_stdout
    @with_payload
    def start(self, image=None, num_workers=None, args=None):
        args = args or []
        remote_image = remote(image)
        docker_utils.docker('pull', remote_image)
        for i in range(int(num_workers)):
            _start(remote_image, args)


def remote(image):
    """Find the name of image in the registry: `LOCAL_REGISTRY`. """

    try:
        registry = os.environ['LOCAL_REGISTRY']
        return '{}/{}'.format(registry, image)
    except KeyError:
        # if LOCAL_REGISTRY is not set, default to docker hub
        return image


def _start(image, args):
    """Start a container from `image`. """

    environment = docker_utils.env(image)
    whitelist = json.loads(environment.get('WHITELIST', '[]'))
    c = docker_utils.docker('run', '-d', image, *args).strip()
    firewall.allow(c, whitelist)
    docker_utils.docker('exec', c, 'touch', '/ready')
    print c

