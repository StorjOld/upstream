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

import sys
import argparse

from exc import FileError
from file import SizeHelpers
from upstream.chunk import Chunk
from upstream.streamer import Streamer


def parse_shard_size(size):
    """ Parse a string, expected to be in the format of, for example:
    250m, 512k, 1024b.  A string without a trailing letter is assumed to be
    bytes. Accepts the following: m as mebibytes, k as kibibytes, b as bytes,


    :param size:
    :return:
    """
    size = str(size)
    if size.isdigit():
        return int(size)
    last = size[-1].lower()
    number = str[:-1]
    choices = ['b', 'k', 'm']
    if last not in choices:
        return
    if last == 'b':
        return int(number)
    elif last == 'k':
        return SizeHelpers.kib_to_bytes(int(number))
    elif last == 'm':
        return SizeHelpers.mib_to_bytes(int(number))


def calculate_shards(shard_size, file):
    file_size = os.path.getsize(file)
    num_shards = int(file_size / shard_size) + 1
    shards = []
    start = 0
    end = shard_size
    for shard in range(num_shards):
        tup = (start, end)
        shards.append(tup)
        start = end
        end += shard_size
    return shards


def upload(args):
    """ Controls actions for uploading

    :param args: Parsed args namespace
    """
    shard_size = parse_shard_size(args.shard_size)

    try:
        filepath = Streamer.check_path(args.file)
    except FileError as e:
        sys.stderr.write('%s\n' % e.message)
        sys.exit(1)

    shards = calculate_shards(shard_size, filepath)  # NOQA
    streamer = Streamer(args.server)

    print("Connecting to %s..." % streamer.server)
    sys.stdout.write("Uploading file...")
    sys.stdout.flush()

    chunk = streamer.upload(args.file)

    sys.stdout.write('Done.\n\n')
    sys.stdout.flush()
    print("File hash: %s" % chunk.filehash)
    print("Decrypt key: %s" % chunk.decryptkey)
    print("URI: %s" % chunk.uri)


def download(args):
    """ Controls actions for downloading

    :param args: Argparse namespace
    """
    print("Creating chunk.")
    chunk = Chunk()
    chunk.from_uri(args.uri)

    streamer = Streamer(args.server)
    print("Connecting to %s..." % streamer.server)
    sys.stdout.write('Downloading file...')
    sys.stdout.flush()
    result = streamer.download(chunk, args.dest, args.chunk_size)
    sys.stdout.write('Done.\n\n')

    if result:
        print("Downloaded to %s." % (args.dest or chunk.filehash))
    else:
        print("Something bad happened.")
        sys.exit(1)


def parse_args():
    """ Parses args

    :return: argparse namespace
    """
    parser = argparse.ArgumentParser("upstream",
                                     description="Command line client for "
                                                 "the Storj web-core API")
    parser.add_argument('--server', default='http://node1.metadisk.org')
    subparser = parser.add_subparsers(dest='action')

    upload_parser = subparser.add_parser('upload',
                                         help="Upload a file from API")
    upload_parser.add_argument('--shard-size',
                               default=SizeHelpers.mib_to_bytes(250),
                               help="Size of shards to break file into and "
                                    "to upload, max: 250m, default: 250m. "
                                    "Ex. 25m - file will be broken into 25 MB "
                                    "chunks and uploaded chunk by chunk")
    upload_parser.add_argument('file')

    download_parser = subparser.add_parser('download',
                                           help="Download a file from API")
    download_parser.add_argument('--uri', required=True,
                                 help="URI of file to download")
    download_parser.add_argument('--dest',
                                 help="Folder or file to download file")
    download_parser.add_argument('--chunk-size', type=int, default=1024)

    return parser.parse_args()


def main():
    args = parse_args()
    if args.action == 'upload':
        upload(args)
    elif args.action == 'download':
        download(args)


if __name__ == '__main__':
    main()
