#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_apim
----------------------------------

Tests for `apim` module.
"""

from textwrap import dedent

import pytest

import apim.adapter

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
