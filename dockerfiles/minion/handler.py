#!/usr/bin/env python
from functools import wraps
import os
import sys
import subprocess
import traceback
import cStringIO

from serf_master import SerfHandler, SerfHandlerProxy


MAX_OUTPUT = 1000


def truncated_stdout(f):
    """Decorator to truncate stdout to final `MAX_OUTPUT` characters. """

    @wraps(f)
    def wrapper(*args, **kwargs):
        old_stdout = sys.stdout
        old_stdout.flush()
        sys.stdout = cStringIO.StringIO()
        out = ''
        try:
            result = f(*args, **kwargs)
            out = 'SUCCESS\n' + sys.stdout.getvalue()
            return result
        except Exception:
            out = 'ERROR\n' + traceback.format_exc()
        finally:
            sys.stdout = old_stdout
            print out[-MAX_OUTPUT:]
    return wrapper


class MinionHandler(SerfHandler):

    @truncated_stdout
    def start(self):
        image, num_workers = sys.stdin.read().split()
        registry = os.environ['LOCAL_REGISTRY']
        remote_image = '{}/{}'.format(registry, image)
        docker('pull', remote_image)
        for i in range(int(num_workers)):
            c = docker('run', '-d', remote_image, 'sleep', 'infinity')
            print c


def path(p):
    """Build the corresponding path `p` inside the container. """

    return os.path.normpath(os.path.join('/host', './{}'.format(p)))


def docker(*args):
    """Execute a docker command inside the container. """

    docker_binary = path(os.environ.get('DOCKER_BINARY', '/usr/bin/docker'))
    docker_socket = path(os.environ.get('DOCKER_SOCKET', '/run/docker.sock'))
    cmd = ('{docker_binary} -H unix://{docker_socket}'
           .format(**locals()).split())
    cmd.extend(args)
    return subprocess.check_output(cmd)


if __name__ == '__main__':
    handler = SerfHandlerProxy()
    handler.register('minion', MinionHandler())
    handler.run()