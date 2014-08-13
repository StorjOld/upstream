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
import unittest

import mock

from upstream.chunk import Chunk
from upstream.streamer import Streamer
from upstream.exc import ConnectError, FileError, ChunkError, ResponseError


class TestChunk(unittest.TestCase):
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
        self.empty_chunk = Chunk()
        # Create half object
        self.half_chunk = Chunk(self.filehash)
        # Create full object
        self.full_chunk = Chunk(self.filehash, self.cryptkey)

        # Create new objects
        self.chunk1 = Chunk()
        self.chunk2 = Chunk()

        # Load content
        self.json_dict = {
            "key": "2b77e64156f9f7eb16d74b98f70417e4"
                   "d665d977d0ef00e793d41767acf13e8c",
            "filehash": "5547a152337de9ff6a97f6f099bb024e"
                        "08af419cee613b18da76a33e581d49ac"
        }
        self.chunk1.from_json(json.dumps(self.json_dict))
        self.chunk2.from_uri(self.raw_uri)

    def tearDown(self):
        del self.empty_chunk
        del self.half_chunk
        del self.full_chunk
        del self.chunk1
        del self.chunk2
        del self.json_dict

    def test_getters_empty_chunk(self):
        def _callable(meth):
            meth = getattr(self.empty_chunk, meth)
            meth()

        for method in ['uri', 'get_hashes', 'get_json']:
            self.assertRaises(ChunkError, _callable, method)

    def test_getters_half_chunk(self):
        def _callable(meth):
            meth = getattr(self.half_chunk, meth)
            meth()

        for method in ['uri', 'get_hashes', 'get_json']:
            self.assertRaises(ChunkError, _callable, method)

    def test_getters_full_chunk(self):
        uri = self.full_chunk.uri
        self.assertEqual(uri, self.raw_uri)
        hash, key = self.full_chunk.get_hashes()
        self.assertEqual(hash, self.filehash)
        self.assertEqual(key, self.cryptkey)
        json_ = self.full_chunk.get_json()
        self.assertEqual(json_, json.dumps(self.json_dict))

    def test_chunks(self):
        # Fit everything into one test case
        self.assertEqual(self.chunk1.get_hashes(), self.chunk2.get_hashes())


class TestStreamer(unittest.TestCase):
    def setUp(self):
        self.stream = Streamer("http://node1.metadisk.org")
        self.orig_hash = None
        self.uploadfile = "tests/1k.testfile"
        self.downloadfile = "download.testfile"
        self.chunk = Chunk(
            "2032e4fd19d4ab49a74ead0984a5f672c26e60da6e992eaf51f05dc874e94bd7",
            "1b1f463cef1807a127af668f3a4fdcc7977c647bf2f357d9fa125f13548b1d14"
        )

    def tearDown(self):
        del self.stream
        del self.orig_hash
        del self.uploadfile
        try:
            os.remove(self.downloadfile)
            os.remove(self.chunk.filehash)
            # pass
        except:
            pass
        del self.downloadfile
        del self.chunk

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
    def test_upload_chunked_encoded(self, post):
        pass

    def test_upload(self):
        # Upload file and check file
        self.chunk = self.stream.upload(self.uploadfile)
        self.assertEqual(
            self.chunk.filehash,
            "2032e4fd19d4ab49a74ead0984a5f672"
            "c26e60da6e992eaf51f05dc874e94bd7")
        self.assertEqual(
            self.chunk.decryptkey,
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
        result = self.stream._upload_check_path(self.uploadfile)
        self.assertEqual(homedir, result)

        with self.assertRaises(FileError) as ex:
            self.stream._upload_check_path('~/does-not-exist')
            self.assertEqual(
                ex.message, '~/does-not-exist not a file or not found')

    def test_download(self):
        result = self.stream.download(self.chunk, self.downloadfile)
        self.assertTrue(result is True)

        orig_sha256 = ("bc839c0f9195028d375d652e72a5d08d"
                       "293eefd22868493185f084bc4aa61d00")
        sha256 = hashlib.sha256()
        with open(self.downloadfile, 'rb') as f:
            sha256.update(f.read())
        new_sha256 = sha256.hexdigest()
        self.assertEqual(orig_sha256, new_sha256)

    def test_download_no_dest(self):
        result = self.stream.download(self.chunk)
        self.assertTrue(result is True)

        orig_sha256 = ("bc839c0f9195028d375d652e72a5d08d"
                       "293eefd22868493185f084bc4aa61d00")
        sha256 = hashlib.sha256()
        with open(self.chunk.filehash, 'rb') as f:
            sha256.update(f.read())
        new_sha256 = sha256.hexdigest()
        self.assertEqual(orig_sha256, new_sha256)

    def test_download_empty_chunk(self):
        chunk = Chunk()
        with self.assertRaises(ChunkError):
            self.stream.download(chunk)

    def test_download_bad_dest(self):
        with self.assertRaises(FileError) as ex:
            self.stream.download(self.chunk, self.uploadfile)
            self.assertEqual(ex.message, "%s already exists" % self.uploadfile)

        with self.assertRaises(FileError) as ex:
            self.stream.download(self.chunk, '/path/does/not/exist.file')
            self.assertEqual(ex.message, '/path/does/not is not a valid path')
