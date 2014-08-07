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
        filehash = ("5547a152337de9ff6a97f6f099bb024e"
                    "08af419cee613b18da76a33e581d49ac")
        decryptkey = ("2b77e64156f9f7eb16d74b98f70417e4"
                      "d665d977d0ef00e793d41767acf13e8c")

        # Create empty object
        empty_chunk = Chunk()
        # Create half object
        half_chunk = Chunk(filehash)
        # Create full object
        full_chunk = Chunk(filehash, decryptkey)

        # Run getters
        self._run_gets(empty_chunk)
        self._run_gets(half_chunk)
        self._run_gets(full_chunk)

        # Create new objects
        self.chunk1 = Chunk()
        self.chunk2 = Chunk()

        # Load content
        json_dict = {
            "key": "2b77e64156f9f7eb16d74b98f70417e4"
                   "d665d977d0ef00e793d41767acf13e8c",
            "filehash": "5547a152337de9ff6a97f6f099bb024e"
                        "08af419cee613b18da76a33e581d49ac"
        }

        self.chunk1.load_json(json.dumps(json_dict))
        raw_uri = ("5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e5"
                   "81d49ac?key=2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef0"
                   "0e793d41767acf13e8c")
        self.chunk2.load_uri(raw_uri)

    def tearDown(self):
        pass

    def _run_gets(self, chunk):
        chunk.get_uri()
        chunk.get_tuple()
        chunk.get_json()

    def test_chunks(self):
        # Fit everything into one test case
        self.assertEqual(self.chunk1.get_tuple(), self.chunk2.get_tuple())


class TestStreamer(unittest.TestCase):
    def setUp(self):
        self.stream = Streamer("http://node1.storj.io")

    def test_upload_chunk(self):
        # Upload file and check file
        self.chunk = self.stream.upload_chunk("C:\\Users\\super3\\Code\\upstream\\test.txt")
        self.assertEqual(
            self.chunk.filehash,
            "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac")
        self.assertEqual(
            self.chunk.decryptkey,
            "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c")

        # Connect to wrong server
        def _failing_connection():
            Streamer("http://blah.storj.io")

        self.assertRaises(LookupError, _failing_connection())

        # Try to upload wrong file
        def _failing_upload():
            self.stream.upload_chunk("blah")
        self.assertRaises(FileNotFoundError, _failing_upload())

    def test_download_chunk(self):
        # Make chunk
        filehash = ("5547a152337de9ff6a97f6f099bb024e08af419c"
                    "ee613b18da76a33e581d49ac")
        decryptkey = ("2b77e64156f9f7eb16d74b98f70417e4d665d9"
                      "77d0ef00e793d41767acf13e8c")
        get_chunk = self.chunk(filehash, decryptkey)

        # Download Chunk
        self.stream.download_chunk(
            get_chunk, "C:\\Users\\super3\\Code\\upstream\\files\\test.txt")

    def test_upload(self):
        # Upload smaller file
        print("Uploading Test 1...")
        self.stream.upload(
            "E:\\Users\\super_000\\Videos\\Planetside2\\PS2Video_0009.avi")

        # Upload smaller file
        print("Uploading Test 2...")
        # Override chunk settings so we don't have a long upload
        self.stream.set_chunk_size(1)
        chunk_list, shredder_data = self.stream.upload(
            "E:\\Users\\super_000\\Videos\\Planetside2\\PS2Video_0009.avi")

        self.chunk_list = chunk_list
        self.shredder_data = shredder_data

    def test_download(self, stream):
        self.stream.download(self.chunk_list, self.shredder_data)