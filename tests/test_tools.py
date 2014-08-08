import time

import pytest

import adama.tools as t

@pytest.fixture(scope='module')
def f():
    def _f(t):
        def __f():
            time.sleep(t)
            return True
        return __f
    return _f

def test_timeout_0(f):
    g = t.TimeoutFunction(f(1), 0)
    assert g()

def test_function_wins(f):
    g = t.TimeoutFunction(f(0.1), 0.2)
    assert g()

def test_timeout_wins(f):
    g = t.TimeoutFunction(f(0.2), 0.1)
    with pytest.raises(t.TimeoutFunctionException):
        g()