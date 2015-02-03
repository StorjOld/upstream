#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014-2015 Paul Durivage, Josh Brandoff for Storj Labs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import setup
from setuptools.command.test import test as TestCommand
import upstream

LONG_DESCRIPTION = open('README.md').read()

install_requirements = [
    'requests-toolbelt',
    'argparse',
    'py3-progressbar==2.4dev',
    'requests',
    'six',
    'storjtorrent',
    'file_encryptor>=0.2.8'
]

test_requirements = [
    'pytest>=2.6.4',
    'pytest-pep8',
    'pytest-cache',
    'mock',
    'coveralls'
]


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import PyTest here because outside, the eggs are not loaded.
        import pytest
        import sys
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name='upstream',
    version=upstream.__version__,
    url='https://github.com/Storj/upstream',
    download_url=''.join(['https://github.com/storj/upstream/tarball/v',
                          upstream.__version__, '-alpha']),
    license=open('LICENSE').read(),
    author='Storj Labs',
    author_email='info@storj.io',
    description='Command line tool for uploading and downloading files from '
                'Metadisk',
    long_description=LONG_DESCRIPTION,
    packages=['upstream'],
    cmdclass={'test': PyTest},
    install_requires=install_requirements,
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'upstream = upstream.clitool:main'
        ]
    },
    keywords=['storj', 'upstream', 'metadisk', 'driveshare', 'farming', 'storjtorrent']
)
