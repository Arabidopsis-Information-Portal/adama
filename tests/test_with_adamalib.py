import adamalib
import pytest


@pytest.fixture(scope='module')
def adama():
    return adamalib.Adama('token', 'http://localhost/community/v0.3')


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