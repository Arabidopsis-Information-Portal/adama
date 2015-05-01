import subprocess
import time

import adamalib
import pytest


@pytest.fixture(scope='module')
def adama():
    return adamalib.Adama('http://localhost/community/v0.3', token='token')


@pytest.fixture(scope='module')
def namespace(adama, request):
    ns = adama.namespaces.add(name='foox')

    def fin():
        ns.delete()

    request.addfinalizer(fin)
    return ns


@pytest.fixture(scope='module')
def json_server(request):
    server = subprocess.Popen('python -m SimpleHTTPServer 1234'.split())
    time.sleep(1)

    def fin():
        server.kill()

    request.addfinalizer(fin)
    return server


@pytest.fixture(scope='module')
def map_service(namespace, request):
    import map_with_adama_obj.main
    srv = namespace.services.add(map_with_adama_obj.main)

    def fin():
        srv.delete()

    request.addfinalizer(fin)
    return srv


def test_namespace(namespace):
    assert namespace.name == 'foox'


def test_query_with_adama_obj(namespace):
    import adapter_with_adama_obj.main
    try:
        srv = namespace.services.add(adapter_with_adama_obj.main)
        assert srv.search()[0]['x'] == 'token'
    finally:
        srv.delete()


def test_multiple_yaml(namespace):
    import adapter_multiple_yaml.main
    try:
        srv = namespace.services.add(adapter_multiple_yaml.main)
        assert srv.endpoints['goo'] == 'hi'
        assert '127.0.0.1' in srv.whitelist
    finally:
        srv.delete()


def test_map(map_service, json_server):
    result = map_service.search()
    assert len(result) == 2
    assert result[0]['x'] == 'token'
