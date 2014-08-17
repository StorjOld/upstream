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
from upstream.exc import ShardError


class Shard(object):
    def __init__(self, filehash=None, decryptkey=None, filename=None,
                 filepath=None):
        """ Stores information about an encryted shard. Allows for
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
        """ Loads object data with information from a URI string in the format
        of ``<hash>?key=<key>``

        :param uri: URI as a string
        :raise ShardError: If not in format of ``<hash>?key=<key>``
        """
        try:
            self.filehash, self.decryptkey = str(uri).split("?key=")
        except:
            raise ShardError("%s not format of <hash>?key=<key>")

    def from_json(self, json_str):
        self.json_str = json_str
        data = json.loads(json_str)
        self.filehash = data['filehash']
        self.decryptkey = data['key']

    @property
    def uri(self):
        """ Property returning a URI-formatted string representation of
        this shard

        :return: URI-formatted string representation of this shard
         :raise ShardError: If filehash or decryptkey not set
        """
        if not self.has_hashes:
            raise ShardError("Filehash or decryptkey not set")
        return self.filehash + "?key=" + self.decryptkey

    def get_hashes(self):
        """ Returns a tuple of (filehash, decryptkey) as strings

        :return: Tuple of (filehash, decryptkey) as strings
        :raise ShardError: If filehash or decryptkey not set
        """
        if not self.has_hashes:
            raise ShardError("Filehash or decryptkey not set")
        return self.filehash, self.decryptkey

    def get_json(self):
        """ Retturns a JSON representation of the filehash and decryptkey

        :return: JSON string of ``{key: <key>, filehash: <filehash>}``
        :raise ShardError:
        """
        if not self.has_hashes:
            raise ShardError("Filehash or decryptkey not set")
        return json.dumps(
            {
                "key":  self.decryptkey,
                "filehash": self.filehash,
            }
        )

    @property
    def has_hashes(self):
        """ Returns boolean indicating whether filehash and decryptkey are
        both set

        :return: Boolean
        """
        return self.filehash and self.decryptkey
