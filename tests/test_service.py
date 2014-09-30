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
        assert state == 'false'
        docker_output('rm', '-f', worker)
