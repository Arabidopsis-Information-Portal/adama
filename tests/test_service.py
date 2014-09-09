#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_adama
----------------------------------

Tests for `adama` module.
"""

import os
import StringIO
from textwrap import dedent

import pytest

import adama.service
from adama.tools import location_of

HERE = location_of(__file__)


def test_log_started():
    lines = dedent(
        """
        foo
        *** WORKER STARTED
        bar
        """)
    s = adama.service.check(lines.splitlines())
    assert s == adama.service.WorkerState.started

def test_log_error():
    lines = dedent(
        """
        foo
        *** WORKER ERROR
        bar
        """)
    s = adama.service.check(lines.splitlines())
    assert s == adama.service.WorkerState.error

def test_log_stalled():
    lines = dedent(
        """
        foo
        spam
        bar
        """)
    s = adama.service.check(lines.splitlines())
    assert s == adama.service.WorkerState.error

def test_log_started_and_failed():
    lines = dedent(
        """
        foo
        *** WORKER STARTED
        spam
        *** WORKER ERROR
        bar
        """)
    s = adama.service.check(lines.splitlines())
    assert s == adama.service.WorkerState.error

def test_adapter_detect_language():
    a = adama.service.Service(
        name='foo', version='', url='http://example.com',
        whitelist=[], description='', requirements=[], notify='',
        adapter='foo.py', code=None)
    assert a.detect_language() == 'python'

    a = adama.service.Service(
        name='foo', version='', url='http://example.com',
        whitelist=[], description='', requirements=[], notify='',
        adapter='foo.rb', code=None)
    assert a.detect_language() == 'ruby'

    a = adama.service.Service(
        name='foo', version='', url='http://example.com',
        whitelist=[], description='', requirements=[], notify='',
        adapter='foo.spam', code=None)
    with pytest.raises(adama.service.APIException):
        a.detect_language()

    a = adama.service.Service(
        name='foo', version='', url='http://example.com',
        whitelist=[], description='', requirements=[], notify='',
        adapter='foo.tgz', code=open(os.path.join(HERE, 'foo.tgz')))
    a.extract_code()
    assert a.detect_language() == 'python'

    a = adama.service.Service(
        name='foo', version='', url='http://example.com',
        whitelist=[], description='', requirements=[], notify='',
        adapter='foo.zip', code=open(os.path.join(HERE, 'foo.zip')))
    a.extract_code()
    assert a.detect_language() == 'ruby'

def test_get_code_module():
    a = adama.service.Service(
        name='foo', version='', url='http://example.com',
        whitelist=[], description='', requirements=[], notify='',
        adapter='foo.py', code=StringIO.StringIO('foo'))
    a.extract_code()
    assert open(
        os.path.join(a.temp_dir, 'user_code/foo.py')).read() == 'foo'

def test_get_code_tarball():
    a = adama.service.Service(
        name='foo', version='', url='http://example.com',
        whitelist=[], description='', requirements=[], notify='',
        adapter='foo.tgz', code=open(os.path.join(HERE, 'foo.tgz')))
    a.extract_code()
    assert open(
        os.path.join(a.temp_dir, 'user_code/main.py')).read() == 'foo\n'
    assert open(
        os.path.join(a.temp_dir, 'user_code/dir/bar')).read() == 'bar\n'

def test_get_code_zip():
    a = adama.service.Service(
        name='foo', version='', url='http://example.com',
        whitelist=[], description='', requirements=[], notify='',
        adapter='foo.zip', code=open(os.path.join(HERE, 'foo.zip')))
    a.extract_code()
    assert open(
        os.path.join(a.temp_dir, 'user_code/main.rb')).read() == 'foo\n'
    assert open(
        os.path.join(a.temp_dir, 'user_code/dir/bar')).read() == 'bar\n'
