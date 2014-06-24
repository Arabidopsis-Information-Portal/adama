from __future__ import print_function

import subprocess
import sys

from .config import Config


def docker(*args):
    host = Config.get('docker', 'host')
    cmd = [Config.get('docker', 'command')] + ['-H', host] if host else []
    return subprocess.check_output(
        cmd + list(args), stderr=subprocess.STDOUT).strip()


def check_docker(display=False):
    """Check that the Docker daemon is running.

    Use the info from the config file.

    """
    try:
        docker('ps')
        return True
    except Exception:
        if display:
            print('No docker daemon listening at {0}'.
                  format(Config.get('docker', 'host')), file=sys.stderr)
            print('or wrong command "{0}"'.
                  format(Config.get('docker', 'command')), file=sys.stderr)
            print('Please, check ~/.apim.conf', file=sys.stderr)
        return False