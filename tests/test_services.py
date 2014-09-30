import os
import tempfile

import pytest
import adama.services
from adama.tools import location_of


HERE = location_of(__file__)


def test_extract_module():
    mod = open(os.path.join(HERE, 'main.py')).read()
    temp = tempfile.mkdtemp()
    user_code = adama.services.extract('mymain.py', mod, temp)
    assert open(os.path.join(user_code, 'mymain.py')).read() == mod


#
#
# def test_get_code_module():
#     a = adama.service.Service(
#         name='foo', namespace='', version='', url='http://example.com',
#         whitelist=[], description='', requirements=[], notify='',
#         json_path='', adapter='foo.py', code='foo', type='QueryWorker')
#     a.extract_code()
#     assert open(
#         os.path.join(a.temp_dir, 'user_code/foo.py')).read() == 'foo'
#
# def test_get_code_tarball():
#     a = adama.service.Service(
#         name='foo', namespace='', version='', url='http://example.com',
#         whitelist=[], description='', requirements=[], notify='',
#         adapter='foo.tgz', code=open(os.path.join(HERE, 'foo.tgz')).read(),
#         json_path='', type='QueryWorker')
#     a.extract_code()
#     assert open(
#         os.path.join(a.temp_dir, 'user_code/main.py')).read() == 'foo\n'
#     assert open(
#         os.path.join(a.temp_dir, 'user_code/dir/bar')).read() == 'bar\n'
#
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
