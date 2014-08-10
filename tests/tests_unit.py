#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014 Paul Durivage <paul.durivage@gmail.com>
# All Rights Reserved

import json
import unittest

from upstream.chunk import Chunk
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
            "f07b1202c982cf8e3e85d80c921a609e"
            "f3321e84373a14579c22359ed888bdc6")
        self.assertEqual(
            self.chunk.decryptkey,
            "2b77e64156f9f7eb16d74b98f70417e4"
            "d665d977d0ef00e793d41767acf13e8c")

        # Connect to wrong server
        def _failing_connection():
            Streamer("http://blah.storj.io")

        self.assertRaises(LookupError, _failing_connection())

        # Try to upload wrong file
        def _failing_upload():
            self.stream.upload("blah")
        self.assertRaises(LookupError, _failing_upload())

    # def test_download_chunk(self):
    #     # Make chunk
    #     filehash = ("f07b1202c982cf8e3e85d80c921a609ef3321e84373a14579c22359ed888bdc6")
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
