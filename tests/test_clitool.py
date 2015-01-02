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

import os
import hashlib
import unittest
import mock

from upstream import clitool
from upstream.shard import Shard
from upstream.streamer import Streamer
from upstream.file import SizeHelpers
from upstream.exc import FileError, ResponseError


class TestClitool(unittest.TestCase):

    def setUp(self):
        self.stream = Streamer("http://node1.metadisk.org")
        self.orig_hash = None
        self.uploadfile = "tests/1k.testfile"
        self.downloadfile = "download.testfile"
        self.shard = Shard(
            "2032e4fd19d4ab49a74ead0984a5f672c26e60da6e992eaf51f05dc874e94bd7",
            "1b1f463cef1807a127af668f3a4fdcc7977c647bf2f357d9fa125f13548b1d14"
        )
        self.args = mock.MagicMock()
        self.args.verbose = False
        self.args.server = 'http://node1.metadisk.org'
        self.args.uri = [self.shard.uri]
        self.args.file = self.uploadfile
        self.args.dest = self.downloadfile
        self.args.shard_size = SizeHelpers.mib_to_bytes(250)

    def tearDown(self):
        del self.stream
        del self.orig_hash
        del self.uploadfile

        if os.path.exists(self.downloadfile):
            os.remove(self.downloadfile)

        if os.path.exists(self.shard.filehash):
            os.remove(self.shard.filehash)

        del self.downloadfile
        del self.shard
        del self.args

    def test_doomed_upload(self):
        self.args.action = 'upload'
        self.args.server = 'http://metadisk.org'
        self.assertRaises(ResponseError, clitool.upload, self.args)

    def test_upload_download(self):
        self.args.action = 'upload'
        clitool.upload(self.args)
        self.args.action = 'download'
        clitool.download(self.args)

        orig_sha256 = ("bc839c0f9195028d375d652e72a5d08d"
                       "293eefd22868493185f084bc4aa61d00")
        sha256 = hashlib.sha256()
        with open(self.downloadfile, 'rb') as f:
            sha256.update(f.read())
        new_sha256 = sha256.hexdigest()
        self.assertEqual(orig_sha256, new_sha256)

    def test_upload_download_with_verbosity(self):
        self.args.verbose = True
        self.args.action = 'upload'
        clitool.upload(self.args)
        self.args.action = 'download'
        clitool.download(self.args)

        orig_sha256 = ("bc839c0f9195028d375d652e72a5d08d"
                       "293eefd22868493185f084bc4aa61d00")
        sha256 = hashlib.sha256()
        with open(self.downloadfile, 'rb') as f:
            sha256.update(f.read())
        new_sha256 = sha256.hexdigest()
        self.assertEqual(orig_sha256, new_sha256)

    def test_upload_bad_file(self):
        self.args.action = 'upload'
        self.args.file = 'notreal'
        with self.assertRaises(SystemExit) as ex:
            clitool.upload(self.args)
        self.assertEqual(ex.exception.code, 1)

    def test_upload_bad_file_with_verbosity(self):
        self.args.action = 'upload'
        self.args.verbose = True
        self.args.file = 'notreal'
        with self.assertRaises(SystemExit) as ex:
            clitool.upload(self.args)
        self.assertEqual(ex.exception.code, 1)

    def test_download_no_dest(self):
        self.args.action = 'download'
        self.args.dest = None
        filepath = clitool.download(self.args)
        self.assertTrue(filepath)
        self.assertTrue(os.path.isfile(filepath))

        orig_sha256 = ("bc839c0f9195028d375d652e72a5d08d"
                       "293eefd22868493185f084bc4aa61d00")
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            sha256.update(f.read())
        new_sha256 = sha256.hexdigest()
        self.assertEqual(orig_sha256, new_sha256)
        os.remove(filepath)

    def test_download_bad_dest(self):
        self.args.action = 'download'
        self.args.dest = 'tests'
        with self.assertRaises(FileError):
            clitool.download(self.args)

    def test_and_get_dest(self):
        path, fname = clitool.check_and_get_dest(self.downloadfile)
        self.assertEqual(os.getcwd(), path)
        self.assertEqual(fname, self.downloadfile)

        with self.assertRaises(FileError):
            path, fname = clitool.check_and_get_dest(self.uploadfile)

        with self.assertRaises(FileError):
            path, fname = clitool.check_and_get_dest('notreal/fakefile')

    def test_and_get_no_dest(self):
        path, fname = clitool.check_and_get_dest(None)
        self.assertTrue(path and fname)

    def test_parse_shard_size(self):
        result = clitool.parse_shard_size('1024')
        self.assertEqual(result, 1024)
        result = clitool.parse_shard_size('1024b')
        self.assertEqual(result, 1024)
        result = clitool.parse_shard_size('1k')
        self.assertEqual(result, 1024)
        result = clitool.parse_shard_size('1m')
        self.assertEqual(result, SizeHelpers.mib_to_bytes(1))
        result = clitool.parse_shard_size('1g')
        self.assertIs(result, None)

    def test_calculate_shards(self):
        shards = clitool.calculate_shards(self.args, 100, self.uploadfile)
        self.assertEqual(len(shards), 11)
        self.assertEqual(shards[0], (0, 100))
        self.assertEqual(shards[-1], (1000, 1100))
