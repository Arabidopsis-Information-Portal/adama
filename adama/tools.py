from contextlib import contextmanager
import itertools
import os
import signal


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


def namespace_of(iden):
    return iden.split('.')[0]


@contextmanager
def chdir(directory):
    old_wd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(old_wd)
