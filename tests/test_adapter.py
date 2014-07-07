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


def test_log_started():
    lines = dedent(
        """
        foo
        *** WORKER STARTED
        bar
        """)
    s = apim.adapter.check(lines.splitlines())
    assert s == apim.adapter.WorkerState.started

def test_log_error():
    lines = dedent(
        """
        foo
        *** WORKER ERROR
        bar
        """)
    s = apim.adapter.check(lines.splitlines())
    assert s == apim.adapter.WorkerState.error

def test_log_stalled():
    lines = dedent(
        """
        foo
        spam
        bar
        """)
    s = apim.adapter.check(lines.splitlines())
    assert s == apim.adapter.WorkerState.error

def test_log_started_and_failed():
    lines = dedent(
        """
        foo
        *** WORKER STARTED
        spam
        *** WORKER ERROR
        bar
        """)
    s = apim.adapter.check(lines.splitlines())
    assert s == apim.adapter.WorkerState.error

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

    a = apim.adapter.Adapter(
        'foo.tgz', open(os.path.join(HERE, 'foo.tgz')).read(), {})
    a.get_code()
    a.detect_language()
    assert a.language == 'python'

    a = apim.adapter.Adapter(
        'foo.zip', open(os.path.join(HERE, 'foo.zip')).read(), {})
    a.get_code()
    a.detect_language()
    assert a.language == 'ruby'

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
        os.path.join(a.temp_dir, 'user_code/main.py')).read() == 'foo\n'
    assert open(
        os.path.join(a.temp_dir, 'user_code/dir/bar')).read() == 'bar\n'

def test_get_code_zip():
    a = apim.adapter.Adapter(
        'foo.zip', open(os.path.join(HERE, 'foo.zip')).read(), {})
    a.get_code()
    assert open(
        os.path.join(a.temp_dir, 'user_code/main.rb')).read() == 'foo\n'
    assert open(
        os.path.join(a.temp_dir, 'user_code/dir/bar')).read() == 'bar\n'
