import os
import multiprocessing
import tempfile
import shutil

import pytest
import adama.services
from adama.tools import location_of
from adama.service_store import service_store
from adama.api import ok


HERE = location_of(__file__)


def test_extract_module():
    mod = open(os.path.join(HERE, 'main.py')).read()
    temp = tempfile.mkdtemp()
    try:
        user_code = adama.services.extract('mymain.py', mod, temp)
        assert open(os.path.join(user_code, 'mymain.py')).read() == mod
    finally:
        shutil.rmtree(temp, ignore_errors=True)

def test_extract_tarball():
    tarball = open(os.path.join(HERE, 'foo.tgz')).read()
    temp = tempfile.mkdtemp()
    try:
        user_code = adama.services.extract('foo.tgz', tarball, temp)
        assert open(
            os.path.join(user_code, 'main.py')).read().startswith('foo')
    finally:
        shutil.rmtree(temp, ignore_errors=True)

def test_extract_zip():
    zipfile = open(os.path.join(HERE, 'foo.zip')).read()
    temp = tempfile.mkdtemp()
    try:
        user_code = adama.services.extract('foo.zip', zipfile, temp)
        assert open(
            os.path.join(user_code, 'main.rb')).read().startswith('foo')
    finally:
        shutil.rmtree(temp, ignore_errors=True)

def test_valid_image_name():
    assert adama.services.valid_image_name('foo')
    assert adama.services.valid_image_name('foo_bar')
    assert adama.services.valid_image_name('foo.baz')
    assert adama.services.valid_image_name('_foo')
    assert adama.services.valid_image_name('foo.0-1')

    assert not adama.services.valid_image_name('fooX')
    assert not adama.services.valid_image_name('foo+')
    assert not adama.services.valid_image_name('Foo')

def test_register():

    q = multiprocessing.Queue()
    def notifier(url, result, data):
        q.put((url, result, data))

    try:
        adama.services.register(
            args={'name': 'post', 'notify': 'http://example.com'},
            namespace='foo_ns',
            user_code=os.path.join(HERE, 'python_test_adapter'),
            notifier=notifier)

        result = q.get(timeout=15)
        assert result[0] == 'http://example.com'
        assert result[1] is ok
        service = result[2]
        assert service.name == 'post'
        assert service.adapter_name == 'post_v0.4'
        assert service.namespace == 'foo_ns'
        assert service.language == 'python'
    finally:
        service_store['foo_ns.post_v0.4']['service'].stop_workers()
        del service_store['foo_ns.post_v0.4']
# def test_get_code_zip():
#     a = adama.service.Service(
#         name='foo', namespace='', version='', url='http://example.com',
#         whitelist=[], description='', requirements=[], notify='',
#         adapter='foo.zip', code=open(os.path.join(HERE, 'foo.zip')).read(),
#         json_path='', type='QueryWorker')
#     a.extract_code()
#     assert open(
#         os.path.join(a.temp_dir, 'user_code/main.rb')).read() == 'foo\n'
#     assert open(
#         os.path.join(a.temp_dir, 'user_code/dir/bar')).read() == 'bar\n'
