#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Paul Durivage for Storj Labs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import setup
import upstream

setup(
    name='upstream',
    version=upstream.__version__,
    url='https://github.com/Storj/upstream',
    license='MIT License',
    author='Storj Labs',
    author_email='info@storj.io',
    description='Command line tool for uploading and downloading files from '
                'Metadisk',
    packages=['upstream'],
    install_requires=[
        'requests-toolbelt',
        'argparse',
        'progressbar==2.4dev',
        'requests',
    ],
    dependency_links=[
        "https://github.com/angstwad/python-progressbar/tarball/master#egg=progressbar-2.4dev"
    ],
    entry_points={
        'console_scripts': [
            'upstream = upstream.clitool:main'
        ]
    },


)
