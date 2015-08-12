import subprocess
import time

import adamalib
import pytest
import requests


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


@pytest.fixture(scope='module')
def generic_service(namespace, request):
    import generic_with_prov.main
    srv = namespace.services.add(generic_with_prov.main)

    def fin():
        srv.delete()

    request.addfinalizer(fin)
    return srv


@pytest.fixture(scope='module')
def passthrough_service(namespace, request):
    import passthrough
    srv = namespace.services.add(passthrough)

    def fin():
        srv.delete()

    request.addfinalizer(fin)
    return srv


@pytest.fixture(scope='module')
def query_service(namespace, request):
    import adapter_with_adama_obj.main
    srv = namespace.services.add(adapter_with_adama_obj.main)

    def fin():
        srv.delete()

    request.addfinalizer(fin)
    return srv


@pytest.fixture(scope='module')
def multiple_yaml(namespace, request):
    import adapter_multiple_yaml.main
    srv = namespace.services.add(adapter_multiple_yaml.main)

    def fin():
        srv.delete()

    request.addfinalizer(fin)
    return srv


@pytest.fixture(scope='module')
def with_exception(namespace, request):
    import adapter_with_exception.main
    srv = namespace.services.add(adapter_with_exception.main)

    def fin():
        srv.delete()

    request.addfinalizer(fin)
    return srv


@pytest.fixture(scope='module')
def with_parameter_validation(namespace, request):
    import test_params.main
    srv = namespace.services.add(test_params.main)

    def fin():
        srv.delete()

    request.addfinalizer(fin)
    return srv


def test_namespace(namespace):
    assert namespace.name == 'foox'


def test_with_parameter_validation(with_parameter_validation):
    res1 = with_parameter_validation.search(x='foo', z=[3,4], w='Spam')
    assert res1[0] == 'x = foo'
    assert res1[1] == 'y = None'
    assert res1[2] == 'z = [3.0, 4.0]'
    assert res1[3] == 'w = Spam'
    assert res1[4] == 'b = True'

    res2 = with_parameter_validation.search(x='foo', z=[3,4], w='Spam', y=1)
    assert res2[1] == 'y = 1'

    res3 = with_parameter_validation.search(x='foo', z=[3,4], w='Spam', y=1, b='no')
    assert res3[4] == 'b = False'

    res3 = with_parameter_validation.search(x='foo', z=[3,4], w='Spam', y=1, b='yes')
    assert res3[4] == 'b = True'
    
    res3 = with_parameter_validation.search(x='foo', z=[3,4], w='Spam', y=1, b=False)
    assert res3[4] == 'b = False'

    with pytest.raises(Exception):
        with_parameter_validation.search(
            x='foo', z=[3,4], w='Spam', y='foo')

    with pytest.raises(Exception):
        with_parameter_validation.search(
            x='foo', z=[3,4], w='Spammy')

    with pytest.raises(Exception):
        with_parameter_validation.search(
            x='foo', w='Spam')


def test_query_with_adama_obj(query_service):
    assert query_service.search()[0]['x'] == 'token'


def test_multiple_yaml(multiple_yaml):
    multiple_yaml.endpoints['goo'] == 'hi'
    assert '127.0.0.1' in multiple_yaml.whitelist


def test_map(map_service, json_server):
    result = map_service.search()
    assert len(result) == 2
    assert result[0]['x'] == 'token'


def test_map_with_prov(map_service, json_server):
    result = map_service.search()
    assert result.prov()


def test_generic_with_prov(generic_service):
    result = generic_service.search()
    assert result.ok
    assert result.links['http://www.w3.org/ns/prov#has_provenance']['url']


def test_passthrough_with_prov(namespace, passthrough_service):
    resp = namespace.passthrough.access()
    assert resp.ok
    assert resp.json()['args'] == {}

def test_tags(multiple_yaml):
    assert multiple_yaml.tags == ['foo', 'bar']


def test_with_exception(with_exception):
    with pytest.raises(Exception):
        with_exception.search(first=True)
    result = with_exception.search()
    assert result[0]['x'] == 5
    assert 'error' in result[1]
    empty_result = with_exception.search(empty=True)
    assert empty_result == []
