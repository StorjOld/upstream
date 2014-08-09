#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


class Chunk:
    def __init__(self, filehash = "", decryptkey = "", filename = "", filepath = ""):
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

    # Loads
    def load_uri(self, raw):
        self.filehash, self.decryptkey = str(raw).split("?key=")
        return self

    def load_json(self, raw):
        self.raw_json = raw
        data = json.loads(raw)
        self.filehash = data['filehash']
        self.decryptkey = data['key']
        return self

    # Gets
    def get_uri(self):
        return self.filehash + "?key=" + self.decryptkey

    def get_tuple(self):
        return (self.filehash, self.decryptkey)

    def get_json(self):
        return json.dumps({"filehash": self.filehash, "key":  self.decryptkey})

    # Extra metadata
    def set_filename(self, filename):
        self.filename = filename

    def set_filepath(self, filepath):
        self.filepath = filepath

    def get_filename(self):
        return self.filename

    def get_filepath(self):
        return self.filepath
