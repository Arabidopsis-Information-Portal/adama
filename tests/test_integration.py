import pytest
import requests
import time
import os
import json

from adama.adapters import adapters
from adama.docker import docker_output
from adama.tools import location_of
HERE = location_of(__file__)

URL = 'http://localhost/adama'
NAMESPACE = 'foox'
SERVICE = 'spam'

TIMEOUT = 120 # seconds

def test_register_namespace():
    resp = requests.post(
        URL, data={'name': NAMESPACE}).json()
    assert resp['status'] == 'success'

    # second time should fail
    resp = requests.post(
        URL, data={'name': NAMESPACE}).json()
    assert resp['status'] == 'error'


def test_register_service():
    code = open(os.path.join(HERE, 'main.py')).read()
    resp = requests.post(URL+'/'+NAMESPACE+'/services',
                  data={'name': SERVICE,
                        'url': URL,
                        'version': 1,
                        'type': 'QueryWorker',
                        'requirements': 'requests'},
                  files={'code': ('main.py', code)})
    response = resp.json()
    assert response['status'] == 'success'

def test_state():
    start = time.time()
    while True:
        if time.time() - start > TIMEOUT:
            assert False
        response = requests.get(
            URL+'/{}/{}_v1'.format(NAMESPACE, SERVICE)).json()
        assert response['status'] == 'success'
        if response['result'].get('service'):
            assert True
            return
        time.sleep(5)

def test_language():
    response = requests.get(
        URL+'/{}/{}_v1'.format(NAMESPACE, SERVICE)).json()
    assert response['status'] == 'success'
    assert response['result']['service']['language'] == 'python'

def test_query():
    response = requests.get(
        URL+'/{}/{}_v1/search?foo=3'.format(NAMESPACE, SERVICE)).json()
    assert response['status'] == 'success'
    result = response['result']
    assert len(result) == 2
    assert result[0]['obj'] == 1
    assert result[1]['obj'] == 2
    assert result[0]['args']['foo'] == ['3']

def test_delete_service():
    resp = requests.delete(
        URL+'/{}/{}_v1'.format(NAMESPACE, SERVICE)).json()
    assert resp['status'] == 'success'

def test_delete_namespace():
    resp = requests.delete(
        URL+'/'+NAMESPACE).json()
    assert resp['status'] == 'success'
