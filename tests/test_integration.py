import pytest
import requests
import subprocess
import time
import os
import json

from adama.docker import docker_output
from adama.tools import location_of
HERE = location_of(__file__)

URL = 'http://localhost'
NAMESPACE = 'foox'
SERVICE = 'spam'
PORT = 1234

TIMEOUT = 60 # seconds

def test_register_namespace():
    resp = requests.post(
        URL+'/namespaces', data={'name': NAMESPACE}).json()
    assert resp['status'] == 'success'

    # second time should fail
    resp = requests.post(
        URL+'/namespaces', data={'name': NAMESPACE}).json()
    assert resp['status'] == 'error'

def test_register_wrong_namespace_name():
    resp = requests.post(
        URL+'/namespaces', data={'name': 'NotValid'}).json()
    assert resp['status'] == 'error'

def test_register_namespace_empty_name():
    resp = requests.post(
        URL+'/namespaces', data={'name': ''}).json()
    assert resp['status'] == 'error'

def test_register_service():
    code = open(os.path.join(HERE, 'main.py')).read()
    resp = requests.post(URL+'/'+NAMESPACE+'/services',
                  data={'name': SERVICE,
                        'url': URL,
                        'version': 1,
                        'type': 'query',
                        'requirements': 'requests'},
                  files={'code': ('main.py', code)})
    response = resp.json()
    assert response['status'] == 'success'

def test_register_service_wrong_name():
    code = open(os.path.join(HERE, 'main.py')).read()
    resp = requests.post(URL+'/'+NAMESPACE+'/services',
                  data={'name': 'NotValid',
                        'url': URL,
                        'version': 1,
                        'type': 'query',
                        'requirements': 'requests'},
                  files={'code': ('main.py', code)})
    response = resp.json()
    assert response['status'] == 'error'

def test_register_processor():
    code = open(os.path.join(HERE, 'main2.py')).read()
    resp = requests.post(URL+'/'+NAMESPACE+'/services',
                  data={'name': SERVICE,
                        'url': 'http://localhost:{}/json.json'.format(PORT),
                        'version': 2,
                        'type': 'map_filter',
                        'json_path': 'results',
                        'whitelist': ['127.0.0.1']},
                  files={'code': ('main.py', code)})
    response = resp.json()
    assert response['status'] == 'success'

    code = open(os.path.join(HERE, 'main3.py')).read()
    resp = requests.post(URL+'/'+NAMESPACE+'/services',
                  data={'name': SERVICE,
                        'url': 'http://localhost:{}/json.json'.format(PORT),
                        'version': 3,
                        'type': 'map_filter',
                        'json_path': 'results',
                        'whitelist': ['127.0.0.1']},
                  files={'code': ('main.py', code)})
    response = resp.json()
    assert response['status'] == 'success'

def test_register_generic():
    code = open(os.path.join(HERE, 'main5.py')).read()
    resp = requests.post(URL+'/'+NAMESPACE+'/services',
                  data={'name': SERVICE,
                        'version': 8,
                        'type': 'generic',
                        'whitelist': ['127.0.0.1']},
                  files={'code': ('main.py', code)})
    response = resp.json()
    assert response['status'] == 'success'

def test_test_register_git_repo():
    subprocess.check_call(
        'tar zxf python_map_filter_test_adapter.tgz'.split())
    resp = requests.post(
        URL+'/'+NAMESPACE+'/services',
        data={'metadata': 'src',
              'git_repository':
                  os.path.join(HERE, 'python_map_filter_test_adapter')})
    response = resp.json()
    assert response['status'] == 'success'

def test_register_git_branch():
    subprocess.check_call(
        'tar zxf branch_adapter.tgz'.split())
    resp = requests.post(
        URL+'/'+NAMESPACE+'/services',
        data={'git_branch': 'FOO',
              'git_repository':
                  os.path.join(HERE, 'branch_adapter')})
    response = resp.json()
    assert response['status'] == 'success'

def test_test_register_git_repo_wrong_name():
    subprocess.check_call(
        'tar zxf wrong_python_test_adapter.tgz'.split())
    resp = requests.post(
        URL+'/'+NAMESPACE+'/services',
        data={'git_repository':
                  os.path.join(HERE, 'wrong_python_test_adapter')})
    response = resp.json()
    assert response['status'] == 'error'

def test_register_passthrough_get():
    resp = requests.post(
        URL+'/'+NAMESPACE+'/services',
        data={'name': SERVICE,
              'type': 'passthrough',
              'version': '6',
              'url': 'http://httpbin.org/get'})
    assert resp.json()['status'] == 'success'

def test_register_passthrough_post():
    resp = requests.post(
        URL+'/'+NAMESPACE+'/services',
        data={'name': SERVICE,
              'type': 'passthrough',
              'version': '7',
              'url': 'http://httpbin.org/post'})
    assert resp.json()['status'] == 'success'

def test_register_passthrough_endpoint():
    resp = requests.post(
        URL+'/'+NAMESPACE+'/services',
        data={'name': SERVICE,
              'type': 'passthrough',
              'version': '10',
              'url': 'http://httpbin.org'})
    assert resp.json()['status'] == 'success'

def test_register_passthrough_via_git():
    subprocess.check_call(
        'tar zxf passthrough_test_adapter.tgz'.split())
    resp = requests.post(
        URL+'/'+NAMESPACE+'/services',
        data={'git_repository':
                os.path.join(HERE, 'passthrough_test_adapter')})
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
        time.sleep(1)

def test_register_wrong_requirements():
    code = open(os.path.join(HERE, 'main4.py')).read()
    resp = requests.post(URL+'/'+NAMESPACE+'/services',
                  data={'name': SERVICE,
                        'url': 'http://localhost:{}/json.json'.format(PORT),
                        'version': 4,
                        'type': 'query',
                        'json_path': 'results',
                        'whitelist': ['127.0.0.1']},
                  files={'code': ('main.py', code)})
    response = resp.json()
    assert response['status'] == 'success'

    start = time.time()
    while True:
        if time.time() - start > TIMEOUT:
            assert False
        response = requests.get(
            URL+'/{}/{}_v4'.format(NAMESPACE, SERVICE)).json()
        assert response['status'] == 'success'
        if response['result'].get('slot') == 'error':
            assert True
            return
        time.sleep(5)

def test_register_unavailable_requirement():
    code = open(os.path.join(HERE, 'main5.py')).read()
    resp = requests.post(URL+'/'+NAMESPACE+'/services',
                  data={'name': SERVICE,
                        'version': 9,
                        'type': 'generic',
                        'requirements': 're',
                        'whitelist': ['127.0.0.1']},
                  files={'code': ('main.py', code)})
    response = resp.json()
    assert response['status'] == 'success'

    start = time.time()
    while True:
        if time.time() - start > TIMEOUT:
            assert False
        response = requests.get(
            URL+'/{}/{}_v9'.format(NAMESPACE, SERVICE)).json()
        assert response['status'] == 'success'
        print response
        if (response['result'].get('slot') == 'error' and
            'No distributions at all found for re' in
                    response['result'].get('msg', '')):
            assert True
            return
        time.sleep(5)

def test_services():
    response = requests.get(
        URL+'/{}/services'.format(NAMESPACE)).json()
    assert response['status'] == 'success'
    results = response['result']
    for result in results:
        if result['name'] == 'spam' and \
            result['version'] == '1' and \
            len(result['workers']) > 0:
            assert True
            return
    assert False

def test_services_in_wrong_namespace():
    response = requests.get(
        URL+'/xxxxxx/services').json()
    assert response['status'] == 'error'

def test_language():
    response = requests.get(
        URL+'/{}/{}_v1'.format(NAMESPACE, SERVICE)).json()
    assert response['status'] == 'success'
    assert response['result']['service']['language'] == 'python'

def test_query():
    response = requests.get(
        URL+'/{}/{}_v1/search?foo=3&bar=baz'.format(NAMESPACE, SERVICE)).json()
    assert response['status'] == 'success'
    result = response['result']
    assert len(result) == 2
    assert result[0]['obj'] == 1
    assert result[1]['obj'] == 2
    assert result[0]['args']['foo'] == '3'
    assert result[0]['args']['bar'] == 'baz'

def test_query_generic():
    response = requests.get(
        URL+'/{}/{}_v8/search?foo=3&bar=baz'.format(NAMESPACE, SERVICE))
    assert response.ok
    assert response.headers['content-type'] == 'text/csv'

def test_list():
    response = requests.get(
        URL+'/{}/{}_v1/list?foo=3'.format(NAMESPACE, SERVICE)).json()
    assert response['status'] == 'success'
    result = response['result']
    assert len(result) == 3
    for i in range(3):
        assert result[i]['i'] == i

def test_process():
    cwd = os.getcwd()
    os.chdir(HERE)
    server = subprocess.Popen('python -m SimpleHTTPServer {}'.format(PORT).split())
    time.sleep(1)  # give some time to web server to start
    try:
        response = requests.get(
            URL+'/{}/{}_v2/search?bar=4'.format(NAMESPACE, SERVICE)).json()
        assert response['status'] == 'success'
        result = response['result']
        assert len(result) == 2
        assert result[0]['other'] == 2
        assert result[1]['other'] == 2

        response = requests.get(
            URL+'/{}/{}_v3/search?bar=4'.format(NAMESPACE, SERVICE)).json()
        assert response['status'] == 'success'
        result = response['result']
        assert len(result) == 1
        assert 'error' in result[0]
    finally:
        server.kill()
        os.chdir(cwd)

def test_git_repo_map_filter():
    start = time.time()
    while True:
        if time.time() - start > TIMEOUT:
            assert False
        response = requests.get(
            URL+'/{}/{}_v5'.format(NAMESPACE, SERVICE)).json()
        assert response['status'] == 'success'
        if response['result'].get('service'):
            break
        time.sleep(1)
    response = requests.get(
        URL+'/{}/{}_v5'.format(NAMESPACE, SERVICE)).json()
    assert response['result']['service']['type'] == 'map_filter'

def test_passthrough_get():
    response = requests.get(
        URL+'/{}/{}_v6/access?bar=4'.format(NAMESPACE, SERVICE)).json()
    assert response['args']['bar'] == '4'

def test_passthrough_post_form():
    response = requests.post(
        URL+'/{}/{}_v7/access?bar=4'.format(NAMESPACE, SERVICE),
        data={'foo': 5}).json()
    assert response['args']['bar'] == '4'
    assert response['form']['foo'] == '5'

def test_passthrough_post_data():
    response = requests.post(
        URL+'/{}/{}_v7/access?bar=4'.format(NAMESPACE, SERVICE),
        data="some text").json()
    assert response['data'] == 'some text'

def test_passthrough_get_extra_fragment():
    response = requests.get(
        URL+'/{}/{}_v10/access/get?foo=3'.format(NAMESPACE, SERVICE)).json()
    assert response['args']['foo'] == '3'

def test_register_with_docs():
    subprocess.check_call(
        'tar zxf test_docs_adapter.tgz'.split())
    resp = requests.post(
        URL+'/'+NAMESPACE+'/services',
        data={'git_repository':
                  os.path.join(HERE, 'test_docs_adapter'),
              'version': 12
              })
    response = resp.json()
    assert response['status'] == 'success'
    while True:
        response = requests.get(
            URL+'/{}/{}_v12'.format(NAMESPACE, SERVICE)).json()
        assert response['status'] == 'success'
        if response['result'].get('service'):
            break
        time.sleep(1)
    response = requests.get(
        URL+'/{}/{}_v12/docs'.format(NAMESPACE, SERVICE)).json()
    assert response['paths']['/search']['get']['description']
    assert response['paths']['/search']['get']['responses']['200']

def test_git_branch_query():
    response = requests.get(
        URL+'/{}/{}_v13/search'.format(NAMESPACE, SERVICE)).json()
    assert response['status'] == 'success'
    assert response['result'][0] == {'foo': 1}

def test_delete_service():
    for i in range(1, 14):
        resp = requests.delete(
            URL+'/{}/{}_v{}'.format(NAMESPACE, SERVICE, i)).json()
        assert resp['status'] == 'success'

def test_delete_namespace():
    resp = requests.delete(
        URL+'/'+NAMESPACE).json()
    assert resp['status'] == 'success'
