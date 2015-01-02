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

import json
import unittest

from upstream.shard import Shard
from upstream.exc import ShardError


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

    def test_shard_with_malformed_uri(self):
        shard = Shard()
        self.assertRaises(ShardError, shard.from_uri, 'funkymonkey')

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
