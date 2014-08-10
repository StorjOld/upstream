#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        if not self.has_hashes():
            return
        return self.filehash, self.decryptkey

    def get_json(self):
        if not self.has_hashes():
            return
        return json.dumps(
            {
                "key":  self.decryptkey,
                "filehash": self.filehash,
            }
        )

    def has_hashes(self):
        return self.filehash and self.decryptkey

    # Extra metadata
    def set_filename(self, filename):
        self.filename = filename

    def set_filepath(self, filepath):
        self.filepath = filepath

    def get_filename(self):
        return self.filename

    def get_filepath(self):
        return self.filepath
