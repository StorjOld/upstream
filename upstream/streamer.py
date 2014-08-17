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

import os
from requests_toolbelt import MultipartEncoder
from file import ShardFile, SizeHelpers

try:
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError

import requests

from upstream.chunk import Chunk
from upstream.exc import FileError, ResponseError, ConnectError, ChunkError


class Streamer(object):

    def __init__(self, server):
        """ For uploading and downloading files from Metadisk.

        :param server: URL to the Metadisk server
        """
        self.server = server
        self.check_connectivity()

    def check_connectivity(self):
        """ Check to see if we even get a connection to the server.
        https://stackoverflow.com/questions/3764291/checking-network-connection
        """
        try:
            urlopen(self.server, timeout=1)
        except URLError:
            raise ConnectError("Could not connect to server.")

    def upload(self, filepath, shard_size=0, start_pos=0, read_size=1024,
               callback=None):
        """ Uploads a chunk via POST to the specified node
        to the web-core API.  See API docs:
        https://github.com/Storj/web-core#api-documentation

        :param filepath: Path to file as a string
        :return: upstream.chunk.Chunk
        :raise LookupError: IF
        """
        # Open the file and upload it via POST
        url = self.server + "/api/upload"  # web-core API
        r = self._upload_form_encoded(
            url,
            filepath,
            shard_size=shard_size,
            start_pos=start_pos,
            read_size=read_size,
            callback=callback
        )

        # Make sure that the API call is actually there
        if r.status_code == 404:
            raise ResponseError("API call not found.")
        elif r.status_code == 402:
            raise ResponseError("Payment required.")
        elif r.status_code == 500:
            raise ResponseError("Server error.")
        elif r.status_code == 201:
            # Everthing checked out, return result
            # based on the format selected
            chunk = Chunk()
            chunk.from_json(r.text)
            return chunk
        else:
            raise ResponseError("Received status code %s %s"
                                % (r.status_code, r.reason))

    def download(self, chunk, dest=None, chunksize=1024):
        """ Downloads a file from the web-core API.

        :param chunk: upstream.chunk.Chunk instance
        :param dest: Path to place file as string, otherwise save to CWD using
        filehash as filename
        :param chunksize: Size of chunks to write to disk in bytes
        :return: True if success, else None
        :raise FileError: If dest is not a valid filepath or if already exists
        """
        try:
            assert chunk.filehash
        except AssertionError:
            raise ChunkError()

        if dest:
            try:
                assert not os.path.exists(dest)
            except AssertionError:
                raise FileError('%s already exists' % dest)

            path, fname = os.path.split(dest)
            if not path:
                path = os.path.abspath(os.getcwd())

            try:
                assert os.path.isdir(path)
            except AssertionError:
                raise FileError('%s is not a valid path' % path)
        else:
            path = os.path.abspath(os.getcwd())
            fname = chunk.filename or chunk.filehash
        savepath = os.path.join(path, fname)
        url = "%s/api/download/%s" % (self.server, chunk.uri)
        resp = requests.get(url, stream=True)
        if resp.status_code == 200:
            with open(savepath, 'wb') as f:
                for chunk in resp.iter_content(chunksize):
                    f.write(chunk)
            return True

    @staticmethod
    def check_path(filepath):
        """ Expands and validates a given path to a file and returns it

        :param filepath: Path to file as string
        :return: Expanded validated path as string
        :raise FileError: If path is not a file or does not exist
        """
        expandedpath = os.path.expanduser(filepath)
        try:
            assert os.path.isfile(expandedpath)
        except AssertionError:
            raise FileError("%s not a file or not found" % filepath)
        return expandedpath

    def _upload_form_encoded(self, url, filepath, shard_size, start_pos,
                             read_size=1024, callback=None):
        """ Streams file from disk and uploads it.

        :param url: API endpoint as URL to upload to
        :param filepath: Path to file as string
        :return: requests.Response
        """
        validpath = self.check_path(filepath)
        if shard_size == 0:
            shard_size = SizeHelpers.mib_to_bytes(250)
        shard = ShardFile(
            validpath, 'rb',
            shard_size=shard_size,
            start_pos=start_pos,
            read_size=read_size,
            callback=callback
        )
        m = MultipartEncoder({
            'file': ('file', shard)
        })
        headers = {
            'Content-Type': m.content_type
        }
        return requests.post(url, data=m, headers=headers)

    def _upload_chunked_encoded(self, url, filepath):
        """ Uploads a file using chunked transfer encoding.
        web-core does not currently accept this type of uploads because
        of issues in upstream projects, primariy flask and werkzeug.  Leaving
        it here for posterity as it might be useful in the future.
        This function currently rases a NotImplementedError currently becuase
        it's purposely "deactivated".

        :param url: API endpoint as URL to upload to
        :param filepath: Path to file as string
        :return: requests.Response
        :raise NotImplementedError: Raises this error on any call.
        """
        raise NotImplementedError
        validpath = self._check_path(filepath)
        return requests.post(url, data=self._filestream(validpath))

    def _filestream(self, filepath):
        """ Streaming file generator

        :param filepath: Path to file to stream
        :raise FileError: If path is not valid
        """
        raise NotImplementedError
        expandedpath = os.path.expanduser(filepath)
        try:
            os.path.isfile(expandedpath)
        except AssertionError:
            raise FileError("%s not a file or not found" % filepath)

        with open(expandedpath, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
