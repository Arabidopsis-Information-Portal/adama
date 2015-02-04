from contextlib import contextmanager
import itertools
import json
import os
import signal

from typing import Dict, List, Union, Undefined, Any, Tuple

from .exceptions import AdamaError


def location_of(filename):
    return os.path.dirname(os.path.abspath(filename))


def interleave(a, b):
    """ '+', [1,2,3] -> [1, '+', 2, '+', 3] """
    yield next(b)
    for x, y in itertools.izip(itertools.cycle(a), b):
        yield x
        yield y


class TimeoutFunctionException(Exception):
    """Exception to raise on a timeout"""
    pass


class TimeoutFunction:

    def __init__(self, function, timeout):
        self.timeout = timeout
        self.function = function

    def handle_timeout(self, signum, frame):
        raise TimeoutFunctionException()

    def __call__(self, *args, **kwargs):
        if self.timeout:
            old = signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.setitimer(signal.ITIMER_REAL, self.timeout, 1)
        try:
            return self.function(*args, **kwargs)
        finally:
            if self.timeout:
                signal.signal(signal.SIGALRM, old)
                signal.setitimer(signal.ITIMER_REAL, 0, 0)


def identifier(namespace, name, version):
    return service_iden(namespace, adapter_iden(name, version))


def adapter_iden(name, version):
    return '{}_v{}'.format(name, version)


def service_iden(namespace, service):
    return '{}.{}'.format(namespace, service)


def namespace_of(identifier):
    return identifier.split('.')[0]


@contextmanager
def chdir(directory):
    old_wd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(old_wd)


def node(role: str) -> Dict[str, Any]:
    try:
        with open('/serfnode/nodes.json') as nodes_file:
            all_nodes = json.load(nodes_file)
            nodes = all_nodes[role]
            nodes.sort(key=lambda obj: float(obj['timestamp']))
            return nodes[0]
    except KeyError:
        raise AdamaError('could not find node with role "{}"'.format(role))
    except FileNotFoundError:
        raise AdamaError('missing info from parent at "/serfnode/nodes.json"')
    except ValueError:
        raise AdamaError('invalid JSON object received from parent')


def location(role: str, port: int) -> Tuple[str, int]:
    info = node(role)
    try:
        port = int(info['ports']['{}/tcp'.format(port)][0])
    except KeyError:
        raise AdamaError('port {}/tcp not found for role {}'
                         .format(port, role))
    return info['ip'], port