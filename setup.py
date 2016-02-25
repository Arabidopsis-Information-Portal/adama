#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand

import os
import sys


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--ignore', 'build']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()

setup(
    name='adama',
    version=open('adama/VERSION').read().strip(),
    description='Araport API manager',
    long_description=readme,
    author='Walter Moreira',
    author_email='wmoreira@tacc.utexas.edu',
    url='https://github.com/waltermoreira/adama',
    packages=[
        'adama'
    ],
    scripts=['bin/adama_server.py'],
    package_dir={'adama': 'adama'},
    include_package_data=True,
    data_files=[('etc', ['adama.conf'])],
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='adama',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    cmdclass={'test': PyTest},
    tests_require=['pytest'],
    test_suite='tests',
)
