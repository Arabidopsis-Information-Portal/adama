#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_apim
----------------------------------

Tests for `apim` module.
"""

import os
from textwrap import dedent

import pytest

import apim.adapter
from apim.tools import location_of

HERE = location_of(__file__)

LOG_STATES = [
    # state, text
    (apim.adapter.STARTED, dedent(
        """
        foo
        *** WORKER STARTED
        bar
        """)),
    (apim.adapter.ERROR, dedent(
        """
        foo
        *** WORKER ERROR
        bar
        """)),
    (apim.adapter.EMPTY, dedent(
        """
        foo
        spam
        bar
        """)),
    (apim.adapter.ERROR, dedent(
        """
        foo
        *** WORKER STARTED
        spam
        *** WORKER ERROR
        bar
        """))
]

@pytest.fixture(scope='module', params=LOG_STATES)
def log(request):
    return request.param

def test_analyze(log):
    state, text = log
    assert apim.adapter.analyze(text) == state

def test_log_started():
    f = lambda *args: LOG_STATES[0][1]
    assert apim.adapter.log_from(None, f) is None

def test_log_error():
    f = lambda *args: LOG_STATES[1][1]
    assert apim.adapter.log_from(None, f) == LOG_STATES[1][1]

def test_log_stalled():
    f = lambda *args: LOG_STATES[2][1]
    assert apim.adapter.log_from(None, f) == LOG_STATES[2][1]

def test_log_started_and_failed():
    f = lambda *args: LOG_STATES[3][1]
    assert apim.adapter.log_from(None, f) == LOG_STATES[3][1]

def test_adapter_detect_language():
    a = apim.adapter.Adapter('foo.py', '', {})
    a.detect_language()
    assert a.language == 'python'

    a = apim.adapter.Adapter('foo.rb', '', {})
    a.detect_language()
    assert a.language == 'ruby'

    a = apim.adapter.Adapter('foo.spam', '', {})
    with pytest.raises(apim.adapter.APIException):
        a.detect_language()

def test_get_code_module():
    a = apim.adapter.Adapter('foo.py', 'foo', {})
    a.get_code()
    assert open(
        os.path.join(a.temp_dir, 'user_code/foo.py')).read() == 'foo'

def test_get_code_tarball():
    a = apim.adapter.Adapter(
        'foo.tgz', open(os.path.join(HERE, 'foo.tgz')).read(), {})
    a.get_code()
    assert open(
        os.path.join(a.temp_dir, 'user_code/foo.py')).read() == 'foo\n'
    assert open(
        os.path.join(a.temp_dir, 'user_code/dir/bar')).read() == 'bar\n'

def test_get_code_zip():
    a = apim.adapter.Adapter(
        'foo.zip', open(os.path.join(HERE, 'foo.zip')).read(), {})
    a.get_code()
    assert open(
        os.path.join(a.temp_dir, 'user_code/foo.py')).read() == 'foo\n'
    assert open(
        os.path.join(a.temp_dir, 'user_code/dir/bar')).read() == 'bar\n'
