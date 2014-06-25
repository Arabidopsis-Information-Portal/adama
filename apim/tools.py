import itertools
import os


def location_of(filename):
    return os.path.dirname(os.path.abspath(filename))


def interleave(a, b):
    """ '+', [1,2,3] -> [1, '+', 2, '+', 3] """
    yield next(b)
    for x, y in itertools.izip(itertools.cycle(a), b):
        yield x
        yield y
