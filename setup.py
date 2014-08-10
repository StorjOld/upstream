#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014 Paul Durivage <paul.durivage@gmail.com>
# All Rights Reserved

from setuptools import setup

setup(
    name='upstream',
    version='0.1.0',
    url='https://github.com/Storj/upstream',
    license='MIT',
    author='Storj Labs',
    author_email='info@storj.io',
    description='Command line tool for uploading and downloading files from Metadisk',
    packages=['upstream'],
    install_requires=[
        'requests',
        'requests-toolbelt'
    ],
    entry_points={
        'console_scripts': [
            'upstream = upstream.clitool:main'
        ]
    },
)
