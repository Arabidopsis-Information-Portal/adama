#!/usr/bin/env python

import subprocess
import sys

from apim.config import Config
from apim.docker import check_docker
from apim.tasks import check_queue


def run_gunicorn():
    subprocess.check_call(
        ['gunicorn',
         '-b', Config.getint('server', 'bind'),
         '-w', Config.get('server', 'workers'),
         '-t', Config.get('server', 'timeout'),
         '-k', 'gevent',
         'apim:app'])


def run():
    """Run the http server."""

    docker_alive = check_docker(display=True)
    queue_alive = check_queue(display=True)
    if not (docker_alive and queue_alive):
        sys.exit(1)

    run_gunicorn()


if __name__ == '__main__':
    run()