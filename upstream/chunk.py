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

import json
from upstream.exc import ChunkError


class Chunk(object):
    def __init__(self, filehash=None, decryptkey=None, filename=None,
                 filepath=None):
        """ Stores information about an encryted chunk. Allows for
        format conversions.

        :param filehash: The hash for a file.
        :param decryptkey: The decryption key for a file.
        :param filename: Name of the file(destroyed on encryption).
        :param filepath:  Location of the file.
        """
        self.filehash = filehash
        self.decryptkey = decryptkey
        self.filename = filename
        self.filepath = filepath

    def from_uri(self, uri):
        """

        :param uri: URI as a string
        :return:
        """
        try:
            self.filehash, self.decryptkey = str(uri).split("?key=")
        except:
            raise ChunkError("%s not format of <hash>?key=<key>")

    def from_json(self, json_str):
        self.json_str = json_str
        data = json.loads(json_str)
        self.filehash = data['filehash']
        self.decryptkey = data['key']

    @property
    def uri(self):
        if not self.has_hashes:
            raise ChunkError("Missing filehash or decryptkey")
        return self.filehash + "?key=" + self.decryptkey

    def get_hashes(self):
        if not self.has_hashes:
            raise ChunkError("Missing filehash or decryptkey")
        return self.filehash, self.decryptkey

    def get_json(self):
        if not self.has_hashes:
            raise ChunkError("Missing filehash or decryptkey")
        return json.dumps(
            {
                "key":  self.decryptkey,
                "filehash": self.filehash,
            }
        )

    @property
    def has_hashes(self):
        return self.filehash and self.decryptkey

    def set_filename(self, filename):
        self.filename = filename

    def set_filepath(self, filepath):
        self.filepath = filepath
