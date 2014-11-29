#!/usr/bin/env python
import json
import sys

import docker_utils
import firewall


def main(*args):
    image = args[0]
    environment = docker_utils.env(image)
    whitelist = json.loads(environment.get('WHITELIST', '[]'))
    c = docker_utils.docker('run', '-d', *args).strip()
    firewall.allow(c, whitelist)
    docker_utils.docker('exec', c, 'touch', '/ready')
    docker_utils.docker('wait', c)


if __name__ == '__main__':
    main(*sys.argv[1:])
