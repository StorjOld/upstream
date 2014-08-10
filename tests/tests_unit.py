#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014 Paul Durivage <paul.durivage@gmail.com>
# All Rights Reserved

import json
import unittest

from upstream.chunk import Chunk
from upstream.exc import ConnectError, FileError
from upstream.streamer import Streamer


class TestChunk(unittest.TestCase):
    def setUp(self):
        # Some values
        self.filehash = ("5547a152337de9ff6a97f6f099bb024e"
                    "08af419cee613b18da76a33e581d49ac")
        self.cryptkey = ("2b77e64156f9f7eb16d74b98f70417e4"
                         "d665d977d0ef00e793d41767acf13e8c")
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
        self.chunk1.load_json(json.dumps(self.json_dict))
        self.chunk2.load_uri(self.raw_uri)

    def tearDown(self):
        del self.empty_chunk
        del self.half_chunk
        del self.full_chunk
        del self.chunk1
        del self.chunk2

    def test_getters_empty_chunk(self):
        result1 = self.empty_chunk.get_uri()
        self.assertIs(result1, None)
        result2 = self.empty_chunk.get_hashes()
        self.assertIs(result2, None)
        result3 = self.empty_chunk.get_json()
        self.assertIs(result3, None)

    def test_getters_half_chunk(self):
        result1 = self.empty_chunk.get_uri()
        self.assertIs(result1, None)
        result2 = self.empty_chunk.get_hashes()
        self.assertIs(result2, None)
        result3 = self.empty_chunk.get_json()
        self.assertIs(result3, None)

    def test_getters_full_chunk(self):
        uri = self.full_chunk.get_uri()
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
        self.stream = Streamer("http://node1.metadisk.org/")

    def tearDown(self):
        del self.stream

    def test_upload(self):
        # Upload file and check file
        self.chunk = self.stream.upload("1k.testfile")
        self.assertEqual(
            self.chunk.filehash,
            "2032e4fd19d4ab49a74ead0984a5f672"
            "c26e60da6e992eaf51f05dc874e94bd7")
        self.assertEqual(
            self.chunk.decryptkey,
            "1b1f463cef1807a127af668f3a4fdcc7"
            "977c647bf2f357d9fa125f13548b1d14")

        # Connect to wrong server
        def _failing_connection():
            Streamer("http://does.not.exist")

        self.assertRaises(ConnectError, _failing_connection)

        # Try to upload wrong file
        def _failing_upload():
            self.stream.upload("not-a-real-file")
        self.assertRaises(FileError, _failing_upload)

    # def test_download_chunk(self):
    #     # Make chunk
    #     filehash = ("bc839c0f9195028d375d652e72a5d08d293eefd22868493185f084bc4aa61d00")
    #     decryptkey = ("2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c")
    #     get_chunk = self.chunk(filehash, decryptkey)
    #
    #     # Download Chunk
    #     self.stream._download_chunk(get_chunk, "/tmp/one_meg.testfile")
    #
    # def test_download(self, stream):
    #     self.stream.download(self.chunk_list, self.shredder_data)


# TODO: Obviously, this should be done
class TestShredder(unittest.TestCase):
    pass
