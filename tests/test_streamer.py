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
import unittest
import mock

from upstream.shard import Shard
from upstream.streamer import Streamer
from upstream.exc import ConnectError, FileError, ShardError, ResponseError


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
        with self.assertRaises(NotImplementedError):
            self.stream._upload_sharded_encoded('http://fake.url', 'fake.path')

    @mock.patch('requests.post')
    def test_filestream(self, post):
        with self.assertRaises(NotImplementedError):
            self.stream._filestream('fake.path')

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
        with self.assertRaises(ResponseError):
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
        self.stream._upload_form_encoded.return_value.reason =\
            "Not Implemented"

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
        r = self.stream.download(self.shard)
        self.assertTrue(r)
        self.assertEquals(r.status_code, 200)
        self.assertEqual(len(r.content), 1024)

    def test_download_exception(self):
        self.shard.filehash = self.shard.filehash[:-5]
        with self.assertRaises(ResponseError) as ex:
            self.stream.download(self.shard)
        self.assertEqual(ex.exception.response.status_code, 404)

    def test_download_empty_shard(self):
        shard = Shard()
        with self.assertRaises(ShardError) as e:
            self.stream.download(shard)
        self.assertEqual(str(e.exception), "Shard missing filehash.")
