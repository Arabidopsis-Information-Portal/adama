#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_adama
----------------------------------

Tests for `adama` module.
"""

import os
from textwrap import dedent

import pytest

import adama.service
from adama.tools import location_of
from adama.docker import docker_output

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
        code_dir=os.path.join(HERE, 'python_test_adapter'))
    assert a.language == 'python'

    a = adama.service.Service(
        code_dir=os.path.join(HERE, 'ruby_test_adapter'))
    assert a.language == 'ruby'

    with pytest.raises(adama.service.APIException):
        a = adama.service.Service(
            code_dir=os.path.join(HERE, 'spam_test_adapter'))

def test_adapter_pyc():
    a = adama.service.Service(
        code_dir=os.path.join(HERE, 'pyc_test_adapter'))
    assert a.language == 'python'
    try:
        os.rename(os.path.join(HERE, 'pyc_test_adapter/src/main.py'),
                  os.path.join(HERE, 'pyc_test_adapter/src/_main.py'))
        assert a.find_main_module().endswith('main.py')
    finally:
        os.rename(os.path.join(HERE, 'pyc_test_adapter/src/_main.py'),
                  os.path.join(HERE, 'pyc_test_adapter/src/main.py'))

def test_workers():
    a = adama.service.Service(
        code_dir=os.path.join(HERE, 'python_test_adapter'))
    a.make_image()
    out = docker_output('inspect', a.iden)
    assert not out.startswith('Error')

    a.start_workers(n=2)
    assert len(a.workers) == 2

    for worker in a.workers:
        state = docker_output('inspect', '-f', '{{.State.Running}}',
                              worker).strip()
        assert state == 'true'

    a.stop_workers()
    for worker in a.workers:
        state = docker_output('inspect', '-f', '{{.State.Running}}',
                              worker).strip()
        assert 'No such image or container' in state

def test_valid_image_name():
    assert adama.service.valid_image_name('foo')
    assert adama.service.valid_image_name('foo_bar')
    assert adama.service.valid_image_name('foo.baz')
    assert adama.service.valid_image_name('_foo')
    assert adama.service.valid_image_name('foo.0-1')

    assert not adama.service.valid_image_name('fooX')
    assert not adama.service.valid_image_name('foo+')
    assert not adama.service.valid_image_name('Foo')

def test_duplicated_in_whitelist():
    a = adama.service.Service(
        code_dir=os.path.join(HERE, 'python_test_adapter'),
        whitelist=['example.com'])
    assert len([x for x in a.whitelist if x == 'example.com']) == 1

def test_passthrough_service():
    a = adama.service.Service(
        code_dir=None, name='foo', namespace='bar', type='passthrough',
        url='http://httpbin.org')
    assert a.check_health()
    assert a.url == 'http://httpbin.org'
