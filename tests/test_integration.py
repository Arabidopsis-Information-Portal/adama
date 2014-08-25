import pytest
import requests
import time
import os
import json

from apim.adapters import adapters
from apim.docker import docker_output
from apim.tools import location_of
HERE = location_of(__file__)

TIMEOUT = 120 # seconds

def test_register():
    code = open(os.path.join(HERE, 'main.py')).read()
    resp = requests.post('http://localhost/register',
                  data={'name': 'foo',
                        'url': 'http://foo.bar',
                        'requirements': 'requests'},
                  files={'code': ('main.py', code)})
    response = resp.json()
    assert response['status'] == 'success'

def test_state():
    start = time.time()
    while True:
        if time.time() - start > TIMEOUT:
            assert False
        response = requests.get('http://localhost/manage/foo_v0.1/state').json()
        assert response['status'] == 'success'
        if response.get('state', None) == 'Ready':
            assert True
            return
        time.sleep(5)

def test_language():
    response = requests.get('http://localhost/register').json()
    assert response['status'] == 'success'
    adapters = response['adapters']
    for adapter in adapters:
        if adapter['identifier'] == 'foo_v0.1':
            assert adapter['language'] == 'python'
            return
    assert False

def test_query():
    resp = requests.post('http://localhost/query',
                 data=json.dumps({
                     'serviceName': 'foo_v0.1',
                     'query': {'foo': 3}
                 }))
    response = resp.json()
    assert response['status'] == 'success'
    result = response['result']
    assert len(result) == 2
    assert result[0]['obj'] == 1
    assert result[1]['obj'] == 2
    assert result[0]['args']['query'] == {'foo': 3}

def test_delete():
    workers = requests.get('http://localhost/register').json()
    assert workers['status'] == 'success'
    for adapter in workers['adapters']:
        workers = adapter['workers']
        if adapter['identifier'] == 'foo_v0.1':
            break
    else:
        assert False

    resp = requests.delete(
        'http://localhost/register',
        data={'name': 'foo_v0.1'})
    response = resp.json()
    assert response['status'] == 'success'

    for worker in workers:
        out = docker_output('inspect', '-f', '{{.State.Running}}', worker)
        assert out.startswith('false')

def test_no_adapter():
    with pytest.raises(KeyError):
        adapters['foo_v0.1']
