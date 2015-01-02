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

import types
import random
import unittest
import pytest
import pdb

from upstream.file import SizeHelpers, ShardFile


def callback(value):
    assert value[0] == 1024
    assert value[1] == 1048576


class TestShardFile(unittest.TestCase):

    def setUp(self):
        self.testfile = 'tests/one-meg.testfile'
        self.shard = ShardFile(self.testfile, 'rb')

    def tearDown(self):
        del self.shard

    def test_instantiation(self):
        self.assertTrue(self.shard._f_obj)
        self.assertTrue(SizeHelpers.mib_to_bytes(25), self.shard.shard_size)
        self.assertEqual(self.shard._f_obj.tell(), 0)
        self.assertEqual(self.shard.filesize, SizeHelpers.mib_to_bytes(1))
        self.assertEqual(self.shard.max_seek, SizeHelpers.mib_to_bytes(1))
        self.assertFalse(hasattr(self.shard, 'callback'))

    def test_iter(self):
        result = self.shard.__iter__()
        self.assertTrue(isinstance(result, types.GeneratorType))

    def test_context_manager(self):
        with ShardFile(self.testfile) as shard:
            self.assertTrue(isinstance(shard, ShardFile))
            self.new_shard = shard
        self.assertTrue(self.new_shard._f_obj.closed)
        del self.new_shard

    def test_next(self):
        result = self.shard.__next__()
        self.assertTrue(result)
        with self.assertRaises(StopIteration):
            while True:
                self.shard.__next__()

    def test_init_callback(self):
        test_shard = ShardFile(self.testfile, 'rb', callback=callback)
        self.assertEqual(test_shard.callback, callback)

    def test__len__(self):
        fivetwelvekay = SizeHelpers.kib_to_bytes(512)
        self.shard.read(fivetwelvekay)
        self.assertTrue(self.shard.__len__() < self.shard.max_seek)

    def test_read_with_size(self):
        fivetwelvekay = SizeHelpers.kib_to_bytes(512)
        read = self.shard.read(fivetwelvekay)
        self.assertEqual(fivetwelvekay, len(read))

    def test_read_no_size(self):
        read = self.shard.read()
        self.assertEqual(len(read), SizeHelpers.mib_to_bytes(1))

    def test_read_loc_is_maxseek(self):
        self.shard.read(self.shard.max_seek)
        read_more = self.shard.read(1)
        self.assertEqual(read_more, '')

    def test_seek(self):
        number = random.randint(1, SizeHelpers.kib_to_bytes(768))
        self.shard.seek(number)
        self.assertEqual(self.shard._f_obj.tell(), number)

    def test_tell(self):
        number = random.randint(1, SizeHelpers.kib_to_bytes(768))
        self.shard.seek(number)
        self.assertEqual(self.shard.tell(), number)

    def test_close(self):
        self.shard._slicegen = None
        self.shard.close()
        self.assertFalse(hasattr(self.shard, '_slicegen'))
        self.assertTrue(self.shard._f_obj.closed)

    def test_generate_slices(self):
        gen = self.shard._generate_slices()
        self.assertTrue(isinstance(gen, types.GeneratorType))

    def test_generate_slices_at_max_seek(self):
        gen = self.shard._generate_slices()
        self.shard.seek(SizeHelpers.mib_to_bytes(1))
        for slice in gen:
            self.assertIs(slice, None)

    def test_generate_slices_near_end(self):
        gen = self.shard._generate_slices()
        self.shard.seek(SizeHelpers.mib_to_bytes(1) - 10)
        for slice in gen:
            self.assertEqual(len(slice), 10)

    def test_generate_slice_read_size(self):
        gen = self.shard._generate_slices()
        for slice in gen:
            self.assertEqual(len(slice), self.shard.read_size)
            break

    def test_generate_slices_callback(self):
        gen = self.shard._generate_slices()
        next(gen)
        self.shard.callback = callback
        next(gen)

    def test_calc_max_seek_near_end(self):
        self.shard.seek(SizeHelpers.mib_to_bytes(1) - 10)
        self.shard._calc_max_seek()
        self.assertEqual(self.shard.max_seek, self.shard.filesize)

    def test_calc_max_seek_beginning_small_shard(self):
        self.shard.shard_size = SizeHelpers.kib_to_bytes(512)
        self.shard._calc_max_seek()
        self.assertEqual(self.shard.max_seek, self.shard.shard_size)

    def test_calc_total_read(self):
        number = random.randint(1, SizeHelpers.mib_to_bytes(1))
        self.shard.seek(number)
        self.shard._calc_total_read()
        self.assertEqual(
            self.shard.total_read_bytes, self.shard.max_seek - number)

    def test_size_helpers_bytes_to_kib(self):
        self.assertEqual(SizeHelpers.bytes_to_kib(1024), 1)

    def test_size_helpers_bytes_to_mib(self):
        self.assertEqual(SizeHelpers.bytes_to_mib(1048576), 1)
