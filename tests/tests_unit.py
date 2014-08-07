#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014 Paul Durivage <paul.durivage@gmail.com>
# All Rights Reserved

import json
import unittest

from upstream.chunk import Chunk


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