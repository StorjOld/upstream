#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import requests
from requests_toolbelt import MultipartEncoder

from upstream.chunk import Chunk
from upstream.exc import FileError, ResponseError, ConnectError, ChunkError

try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve
try:
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.retrieve import urlopen, URLError


class Streamer(object):

    def __init__(self, server):
        """ For uploading and downloading files from Metadisk.

        :param server: URL to the Metadisk server
        """
        self.server = server
        self.check_connectivity()

    def check_connectivity(self):
        """
        Check to see if we even get a connection to the server.
        https://stackoverflow.com/questions/3764291/checking-network-connection

        """
        try:
            urlopen(self.server, timeout=1)
        except URLError:
            raise ConnectError("Could not connect to server.")

    def upload(self, filepath):
        """ Uploads a chunk via POST to the specified node
        to the web-core API.  See API docs:
        https://github.com/Storj/web-core#api-documentation

        :param filepath: Path to file as a string
        :return: upstream.chunk.Chunk
        :raise LookupError: IF
        """
        # Open the file and upload it via POST
        url = self.server + "/api/upload"  # web-core API
        r = self._upload_form_encoded(url, filepath)

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
            return chunk.load_json(r.text)
        else:
            raise ResponseError("Received status code %s %s"
                                % (r.status_code, r.reason))

    def download(self, chunk_list, shredder_data=None, destination=""):
        """Download a chunk via GET from the specified node.

        :param chunk_list:
        :param shredder_data:
        :param destination:
        """
        if len(chunk_list) <= 0:
            pass
        elif len(chunk_list) == 1:
            self._download_chunk(chunk_list[0], destination)
        else:
            for chunk in chunk_list:
                self._download_chunk(chunk, "download/" + chunk.filename)
            shredder_data.merge_chunks()

    def check_path(self, filepath):
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

    def _upload_form_encoded(self, url, filepath):
        """ Streams file from disk and uploads it.

        :param url: API endpoint as URL to upload to
        :param filepath: Path to file as string
        :return: requests.Response
        """
        validpath = self.check_path(filepath)
        m = MultipartEncoder(
            {
                'file': ('testfile', open(validpath, 'rb'))
            }
        )
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
        # validpath = self._check_path(filepath)
        # return requests.post(url, data=self._filestream(validpath))
        raise NotImplementedError

    def _download_chunk(self, chunk, destination=""):
        """ Download a chunk via GET from the specified node.
        https://github.com/storj/web-core

        :param chunk: Information about the chunk to download.
        :param destination: Path where we store the file.
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

    def _filestream(self, filepath):
        """ Streaming file generator

        :param filepath: Path to file to stream
        :raise FileError: If path is not valid
        """
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
