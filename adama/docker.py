from __future__ import print_function

import os
import random
import subprocess
import sys

from .api import APIException
from .config import Config
from .tools import TimeoutFunction, TimeoutFunctionException


# max length of the identifier for the virtual iface
VETH_LENGTH = 14
# max number of attempts to try to find a free ip
MAX_ATTEMPTS = 10

def docker(*args, **kwargs):
    host = Config.get('docker', 'host')
    cmd = [Config.get('docker', 'command')] + (['-H', host] if host else [])
    stderr = kwargs.get('stderr', subprocess.STDOUT)
    stdout = kwargs.get('stdout', sys.stdout)
    return subprocess.Popen(
        cmd + list(args), stdout=stdout, stderr=stderr)


def safe_docker(*args):
    """Execute docker and raise exception with stderr&stdout if failed."""

    proc = docker(*args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    out, _ = proc.communicate()
    if proc.returncode:
        raise APIException(out)


def docker_output(*args):
    p = docker(*args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    return p.communicate()[0]


def tail(fd, timeout=0, process=None):
    f = os.fdopen(fd, 'r', 0)
    readline = TimeoutFunction(f.readline, timeout)
    try:
        while True:
            yield readline()
    except TimeoutFunctionException:
        return
    finally:
        f.close()
        if process is not None:
            process.kill()


def tail_logs(container, timeout=0):
    r, w = os.pipe()
    logs = docker('logs', '-f', container, stderr=subprocess.STDOUT, stdout=w)
    return tail(r, timeout, process=logs)


def check_docker(display=False):
    """Check that the Docker daemon is running.

    Use the info from the config file.

    """
    try:
        docker_output('ps')
        return True
    except Exception:
        if display:
            print('No docker daemon listening at {0}'.
                  format(Config.get('docker', 'host')), file=sys.stderr)
            print('or wrong command "{0}"'.
                  format(Config.get('docker', 'command')), file=sys.stderr)
            print('Please, check ~/.adama.conf', file=sys.stderr)
        return False


def start_container(iden, *params):
    """Run container from image ``iden``."""

    container = docker_output('run', '-d', iden, *params).strip()
    return container
