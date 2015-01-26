from contextlib import contextmanager
import itertools
import json
import os
import signal

from typing import typevar, Dict, List, Union, Undefined

from .exceptions import AdamaError


FileNotFoundError = Undefined(Exception)
Ports = typevar('Ports', values=(Dict[str, List[str]],))
NodeInfo = typevar('NodeInfo', values=(Dict[str, Union[str, Ports]],))


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


def node(role: str) -> NodeInfo:
    try:
        with open('/serfnode/nodes.json') as nodes_file:
            nodes = json.load(nodes_file)
            return nodes[role]
    except KeyError:
        raise AdamaError('could not find node with role "{}"'.format(role))
    except FileNotFoundError:
        raise AdamaError('missing info from parent at "/serfnode/nodes.json"')
    except ValueError:
        raise AdamaError('invalid JSON object received from parent')
