from contextlib import contextmanager
import os


def identifier(namespace, name, version):
    return '{}.{}_v{}'.format(namespace, name, version)


@contextmanager
def chdir(directory):
    old_wd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(old_wd)

