#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


class ShardFile(object):
    """ A custom file-like object where files can be read as shards, i.e. a
    file can be sharded by multiple processes, each with their own start
    and end point.  ShardFile is an iterator, and therefore supports use
    in ``for-in`` loops.  For example, you could grap a shard starting at
    an index of 25 MB into the file, grabbing from 25-50 MB, with each
    loop in a for loop scraping 1024 bytes at a time.  This makes streaming
    files from disk out over a network a breeze.  This class also accepts
    an option callback function, which will invoke the callback with a tuple
    of ints in the form of (current_position, reading_total). Both values are
    in bytes.

    Usage::

        shard = ShardFile('/path/to/file', 'rb', shard_size=65536)
        for slice in shard:
            do_something(with=slice)

    """
    def __init__(self, filename, mode='r', buffering=-1, shard_size=262144000,
                 start_pos=0, read_size=1024, callback=None):
        """ Initializes with sane defaults similar to the builtin function
        *open*.
        :param filename: Path to file as string
        :param mode: File mode with which to open the file; accepts same modes
        as builtin function *open*. Defaults to file builtin's mode of 'r'.
        :param buffering: Type of buffering to use. Accepts same values as file
        builtin function. Defaults to -1.
        :param shard_size: Size of the shard to open and work with in bytes.
        :param start_pos: Point at which to start this shard in bytes.
        :param read_size: The size of the 'slice' to read and yield in the
        generator method
        :param callback: The optional callback will invoke the callback with
        a tuple of ints in the form of (current_position, reading_total).
        Both values are in bytes.
        """
        self._f_obj = open(filename, mode, buffering)
        self.shard_size = shard_size
        self._f_obj.seek(start_pos)
        self.read_size = read_size
        self.filesize = os.path.getsize(filename)

        self.max_seek = None
        self._calc_max_seek()
        self._calc_total_read()
        if callable(callback):
            self.callback = callback

    def __iter__(self):
        return self._generate_slices()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self._f_obj.close()

    def __len__(self):
        return abs(self.tell() - self.total_read_bytes)

    def next(self):
        if not hasattr(self, '_slicegen'):
            self._slicegen = self._generate_slices()
        result = next(self._slicegen)
        if not result:
            raise StopIteration
        return result

    # Py3 Support
    __next__ = next

    def read(self, size=None):
        """ Reads the value of size from the file object and returns.  Will
        not read more than the maximum size of the shard, stored in the
        max_seek attribute.

        :param size: Size in bytes to read
        :return: Bytes ready from file object stream
        :raise IOError: If exceeding the max_seek attribute
        """
        self._callback()
        if size:
            loc = self.tell()
            if loc == self.max_seek:
                return ''
            elif size + loc > self.max_seek:
                size = self.max_seek - loc
                return self._f_obj.read(size)
            else:
                return self._f_obj.read(size)
        return self._f_obj.read(self.max_seek)

    def seek(self, *args, **kwargs):
        """ Calls directly to the file object's seek method.

        :param args: positional args
        :param kwargs: keword args
        """
        self._f_obj.seek(*args, **kwargs)

    def tell(self):
        """ Returns the current position of the cursor in the file object

        :return: Return value of the file object tell() method
        """
        return self._f_obj.tell()

    def close(self):
        """ Closes the file stream

        :return: The return value of close call to file object
        """
        if hasattr(self, '_slicegen'):
            del self._slicegen
        return self._f_obj.close()

    def _generate_slices(self):
        """ This method is called by the __iter__ method to provide an
        iter-compatible generator to stream slices of shards from disk.
        Also used by the next() method.

        """
        while True:
            self._callback()
            loc = self.tell()
            if loc == self.max_seek:
                # We've reached the end of this shard: return.
                return
            elif loc + self.read_size > self.max_seek:
                # The shardsize will exceed the max position, so
                # only yield what's left
                diff = self.max_seek - loc
                yield self._f_obj.read(diff)
            else:
                yield self._f_obj.read(self.read_size)

    def _calc_max_seek(self):
        """ Calculates the maximum postion to seek.
        Sets the max_seek attribute.
        """
        loc = self._f_obj.tell()
        if loc + self.shard_size > self.filesize:
            self.max_seek = self.filesize
        else:
            self.max_seek = loc + self.shard_size

    def _calc_total_read(self):
        """ Calculates the total amount of data to be read.
        Sets the total_read_bytes attribute.
        """
        loc = self._f_obj.tell()
        self.total_read_bytes = self.max_seek - loc

    def _callback(self):
        do_callback = hasattr(self, 'callback')
        loc = self._f_obj.tell()
        if do_callback:
            if loc < self.total_read_bytes:
                self.callback((loc, self.total_read_bytes))


class SizeHelpers(object):
    @staticmethod
    def bytes_to_kib(value):
        return value / 1024

    @staticmethod
    def bytes_to_mib(value):
        return value / 1024 / 1024

    @staticmethod
    def mib_to_bytes(value):
        return value * 1024 * 1024

    @staticmethod
    def kib_to_bytes(value):
        return value * 1024
