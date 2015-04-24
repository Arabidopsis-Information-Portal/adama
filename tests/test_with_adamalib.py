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