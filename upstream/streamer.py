#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve
try:
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.retrieve import urlopen, URLError

import requests

import shredder
import upstream


class Streamer:
    def __init__(self, server, chunk_size = 32):
        """
        For uploading and downloading files from Metadisk.

        Params:
            server -- URL to the Metadisk server.

        """
        self.server = server
        self.check_connectivity()
        self.chunk_size = chunk_size * 1048576

    def get_server(self):
        """Get the current server we are connecting to."""
        return self.server

    def set_server(self, server):
        """Set the current server we are connecting to."""
        self.server = server

    def get_chunk_size(self, units = "MB"):
        """Get the current chunk size."""
        if units == "MB": return (self.chunk_size / 1048576) # B to MB
        else: return self.chunk_size

    def set_chunk_size(self, chunk_size, units = "MB"):
        """Set the current chunk size."""
        if units == "MB": self.chunk_size = chunk_size * 1048576 # MB to B
        else: self.chunk_size = chunk_size

    def check_connectivity(self):
        """
        Check to see if we even get a connection to the server.
        https://stackoverflow.com/questions/3764291/checking-network-connection

        """
        try:
            urlopen(self.server, timeout=1)
        except URLError:
            raise LookupError("Could not connect to server.")

    def upload(self, path):
        """Uploads a chunk via POST to the specified node."""
        chunk_list = []
        shredder_data = shredder.Shredder(path, self.chunk_size)

        # megabytes to bytes to see if its smaller than a chunk
        if os.path.getsize(path) < self.chunk_size:
            # regular upload
            chunk_list.append(self.upload_chunk(path))
        else:
            # split the file into chunk_size peices
            peices = shredder_data.shred_chunks()

            for peice in peices:
                filepath = os.path.abspath(peice)
                filename = os.path.split(peice)[1]

                chunk = self.upload_chunk(peice)
                os.remove(filepath) # remove tmp peice file

                # filename, hash, decrypt key
                chunk.set_filepath(filepath)
                chunk.set_filename(filename)

                chunk_list.append(chunk)

        return chunk_list, shredder_data

    def download(self, chunk_list, shredder_data = None, destination=""):
        """Download a chunk via GET from the specified node."""

        if len(chunk_list) <= 0:
            pass
        elif len(chunk_list) == 1:
            self.download_chunk(chunk_list[0], destination)
        else:
            for chunk in chunk_list:
                self.download_chunk(chunk, "download/" + chunk.filename)
            shredder_data.merge_chunks()

    def upload_chunk(self, path):
        """
        Uploads a chunk via POST to the specified node.
        https://github.com/storj/web-core

        Params:
            path -- The path to the file you want to upload.

        """
        # Open the file and upload it via POST
        files = {'file': open(path, 'rb')}
        url = self.server + "/api/upload" # web-core API
        r = requests.post(url, files=files)

        # Make sure that the API call is actually there
        if r.status_code == 404:
            raise LookupError("API call not found.")
        elif r.status_code == 402:
            raise LookupError("Payment required.")
        elif r.status_code == 500:
            raise LookupError("Server error.")
        elif r.status_code == 201:
            # Everthing checked out, return result
            # based on the format selected
            return upstream.chunk().load_json(r.text)
        else:
            raise LookupError("Unknown status code.")

    def download_chunk(self, chunk, destination=""):
        """
        Download a chunk via GET from the specified node.
        https://github.com/storj/web-core

        Params:
            chunk -- Information about the chunk to download.
            destination(optional) -- Path where we store the file.

        """

        # Generate request URL
        if chunk.decryptkey == "":
            url = self.server + "/api/download/" + chunk.filehash
        else:
            url = self.server + "/api/download/" + chunk.get_uri()

        # Retrieve chunk from the server and pass it the default file directory
        # or override it to a particular place
        if destination == "":
            return urlretrieve(url, "files/" + chunk.filehash)
        else:
            return urlretrieve(url, destination)
