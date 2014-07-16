from __future__ import print_function

import os
import select
import subprocess
import sys

from .config import Config
from .tools import TimeoutFunction, TimeoutFunctionException


def docker(*args, **kwargs):
    host = Config.get('docker', 'host')
    cmd = [Config.get('docker', 'command')] + (['-H', host] if host else [])
    stderr = kwargs.get('stderr', subprocess.STDOUT)
    stdout = kwargs.get('stdout', subprocess.STDOUT)
    return subprocess.Popen(
        cmd + list(args), stdout=stdout, stderr=stderr)

def docker_output(*args):
    p = docker(*args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    return p.communicate()[0]

def tail(fd, timeout=0):
    f = os.fdopen(fd, 'r', 0)
    readline = TimeoutFunction(f.readline, timeout)
    try:
        while True:
            yield readline()
    except TimeoutFunctionException:
        return
    finally:
        f.close()

def tail_logs(container, timeout=0):
    r, w = os.pipe()
    p = docker('logs', '-f', container, stderr=subprocess.STDOUT, stdout=w)
    return tail(r, timeout)


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
            print('Please, check ~/.apim.conf', file=sys.stderr)
        return False