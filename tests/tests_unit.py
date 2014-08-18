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

import os
import json
import hashlib
import random
import types
import unittest

try:
    import mock
except ImportError:
    from unittest import mock

from upstream.shard import Shard
from upstream.streamer import Streamer
from upstream.file import ShardFile, SizeHelpers
from upstream.exc import ConnectError, FileError, ShardError, ResponseError


class TestShard(unittest.TestCase):
    def setUp(self):
        self.cryptkey = ("2b77e64156f9f7eb16d74b98f70417e4"
                         "d665d977d0ef00e793d41767acf13e8c")
        self.filehash = ("5547a152337de9ff6a97f6f099bb024e"
                         "08af419cee613b18da76a33e581d49ac")
        self.raw_uri = (
            "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
            "?key=2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf"
            "13e8c")

        # Create empty object
        self.empty_shard = Shard()
        # Create half object
        self.half_shard = Shard(self.filehash)
        # Create full object
        self.full_shard = Shard(self.filehash, self.cryptkey)

        # Create new objects
        self.shard1 = Shard()
        self.shard2 = Shard()

        # Load content
        self.json_dict = {
            "key": "2b77e64156f9f7eb16d74b98f70417e4"
                   "d665d977d0ef00e793d41767acf13e8c",
            "filehash": "5547a152337de9ff6a97f6f099bb024e"
                        "08af419cee613b18da76a33e581d49ac"
        }
        self.shard1.from_json(json.dumps(self.json_dict))
        self.shard2.from_uri(self.raw_uri)

    def tearDown(self):
        del self.empty_shard
        del self.half_shard
        del self.full_shard
        del self.shard1
        del self.shard2
        del self.json_dict

    def test_getters_empty_shard(self):
        def _callable(meth):
            meth = getattr(self.empty_shard, meth)
            meth()

        for method in ['uri', 'get_hashes', 'get_json']:
            self.assertRaises(ShardError, _callable, method)

    def test_getters_half_shard(self):
        def _callable(meth):
            meth = getattr(self.half_shard, meth)
            meth()

        for method in ['uri', 'get_hashes', 'get_json']:
            self.assertRaises(ShardError, _callable, method)

    def test_getters_full_shard(self):
        uri = self.full_shard.uri
        self.assertEqual(uri, self.raw_uri)
        hash, key = self.full_shard.get_hashes()
        self.assertEqual(hash, self.filehash)
        self.assertEqual(key, self.cryptkey)
        json_ = self.full_shard.get_json()
        self.assertEqual(json_, json.dumps(self.json_dict))

    def test_shards(self):
        # Fit everything into one test case
        self.assertEqual(self.shard1.get_hashes(), self.shard2.get_hashes())


class TestStreamer(unittest.TestCase):
    def setUp(self):
        self.stream = Streamer("http://node1.metadisk.org")
        self.orig_hash = None
        self.uploadfile = "tests/1k.testfile"
        self.downloadfile = "download.testfile"
        self.shard = Shard(
            "2032e4fd19d4ab49a74ead0984a5f672c26e60da6e992eaf51f05dc874e94bd7",
            "1b1f463cef1807a127af668f3a4fdcc7977c647bf2f357d9fa125f13548b1d14"
        )

    def tearDown(self):
        del self.stream
        del self.orig_hash
        del self.uploadfile
        try:
            os.remove(self.downloadfile)
        except:
            pass
        try:
            os.remove(self.shard.filehash)
        except:
            pass
        del self.downloadfile
        del self.shard

    def test_initialization(self):
        self.assertEqual(self.stream.server, "http://node1.metadisk.org")

    def test_check_connectivity(self):
        def _failing_connection():
            Streamer("http://does.not.exist")

        self.assertRaises(ConnectError, _failing_connection)

    @mock.patch('requests.post')
    def test_upload_form_encoded(self, post):
        pass

    @mock.patch('requests.post')
    def test_upload_sharded_encoded(self, post):
        pass

    def test_upload(self):
        # Upload file and check file
        self.shard = self.stream.upload(self.uploadfile)
        self.assertEqual(
            self.shard.filehash,
            "2032e4fd19d4ab49a74ead0984a5f672"
            "c26e60da6e992eaf51f05dc874e94bd7")
        self.assertEqual(
            self.shard.decryptkey,
            "1b1f463cef1807a127af668f3a4fdcc7"
            "977c647bf2f357d9fa125f13548b1d14")

        # Try to upload wrong file
        def _failing_upload():
            self.stream.upload("not-a-real-file")
        self.assertRaises(FileError, _failing_upload)

    def test_upload_patched_404(self):
        self.stream._upload_form_encoded = mock.MagicMock()
        self.stream._upload_form_encoded.return_value()
        self.stream._upload_form_encoded.return_value.status_code = 404

        def _fourohfour():
            self.stream.upload(self.uploadfile)
        with self.assertRaises(ResponseError) as ex:
            _fourohfour()
            self.assertEqual(ex.message, "API call not found.")

    def test_upload_patched_402(self):
        self.stream._upload_form_encoded = mock.MagicMock()
        self.stream._upload_form_encoded.return_value()
        self.stream._upload_form_encoded.return_value.status_code = 402

        def _fourohtwo():
            self.stream.upload(self.uploadfile)
        with self.assertRaises(ResponseError) as ex:
            _fourohtwo()

    def test_upload_patched_500(self):
        self.stream._upload_form_encoded = mock.MagicMock()
        self.stream._upload_form_encoded.return_value()
        self.stream._upload_form_encoded.return_value.status_code = 500

        def _fivehundred():
            self.stream.upload(self.uploadfile)
        with self.assertRaises(ResponseError) as ex:
            _fivehundred()
            self.assertEqual(ex.message, "Server error.")

    def test_upload_patched_501(self):
        self.stream._upload_form_encoded = mock.MagicMock()
        self.stream._upload_form_encoded.return_value()
        self.stream._upload_form_encoded.return_value.status_code = 501
        self.stream._upload_form_encoded.return_value.reason = "Not Implemented"

        def _fiveohone():
            self.stream.upload(self.uploadfile)
        with self.assertRaises(ResponseError) as ex:
            _fiveohone()
            self.assertEqual(ex.message,
                             "Received status code 501 Not Implemented")

    def test_upload_check_path(self):
        homedir = os.path.expanduser(self.uploadfile)
        result = self.stream.check_path(self.uploadfile)
        self.assertEqual(homedir, result)

        with self.assertRaises(FileError) as ex:
            self.stream.check_path('~/does-not-exist')
            self.assertEqual(
                ex.message, '~/does-not-exist not a file or not found')

    def test_download(self):
        result = self.stream.download([self.shard], self.downloadfile)
        self.assertTrue(result)

        orig_sha256 = ("bc839c0f9195028d375d652e72a5d08d"
                       "293eefd22868493185f084bc4aa61d00")
        sha256 = hashlib.sha256()
        with open(self.downloadfile, 'rb') as f:
            sha256.update(f.read())
        new_sha256 = sha256.hexdigest()
        self.assertEqual(orig_sha256, new_sha256)

    def test_download_no_dest(self):
        result = self.stream.download([self.shard])
        self.assertTrue(result)

        orig_sha256 = ("bc839c0f9195028d375d652e72a5d08d"
                       "293eefd22868493185f084bc4aa61d00")
        sha256 = hashlib.sha256()
        with open(result, 'rb') as f:
            sha256.update(f.read())
        new_sha256 = sha256.hexdigest()
        self.assertEqual(orig_sha256, new_sha256)

    def test_download_empty_shard(self):
        shard = Shard()
        with self.assertRaises(ShardError):
            self.stream.download([shard])

    def test_download_bad_dest(self):
        with self.assertRaises(FileError) as ex:
            self.stream.download([self.shard], self.uploadfile)
            self.assertEqual(ex.message, "%s already exists" % self.uploadfile)

        with self.assertRaises(FileError) as ex:
            self.stream.download([self.shard], '/path/does/not/exist.file')
            self.assertEqual(ex.message, '/path/does/not is not a valid path')
