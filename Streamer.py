import os
import json
import requests
import argparse
import urllib.request
from urllib.parse import urlsplit

from Chunk import Chunk
from Shredder import Shredder

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
		return server

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
			urllib.request.urlopen(self.server, timeout=1)
		except urllib.request.URLError:
			raise LookupError("Could not connect to server.")

	def upload(self, path):
		"""Uploads a chunk via POST to the specified node."""
		chunk_list = []
		shredder_data = Shredder(path, self.chunk_size)

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
			return Chunk().load_json(r.text)
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

		# Retreive chunk from the server and pass it the default file directory
		# or override it to a particular place
		if destination == "":
			return urllib.request.urlretrieve(url, "files/" + chunk.filehash)
		else:
			return urllib.request.urlretrieve(url, destination)


# Unit Testing
def unit_test_upload_chunk(stream):
	# Upload file and check file
	chunk = stream.upload_chunk("C:\\Users\\super3\\Code\\upstream\\test.txt")
	assert(chunk.filehash == "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac")
	assert(chunk.decryptkey == "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c")

	# Connect to wrong server
	try:
		test = Streamer("http://blah.storj.io")
	except LookupError:
		assert(True)
	else:
		assert(False)

	# Try to upload wrong file
	try:
		chunk = stream.upload_chunk("blah")
	except FileNotFoundError:
		assert(True)
	else:
		assert(False)

def unit_test_download_chunk(stream):
	# Make chunk
	filehash = "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
	decryptkey = "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c"
	get_chunk = Chunk(filehash, decryptkey)

	# Download Chunk
	stream.download_chunk(get_chunk, "C:\\Users\\super3\\Code\\upstream\\files\\test.txt")

def unit_test_upload(stream):
	# Upload smaller file
	print("Uploading Test 1...")
	stream.upload("E:\\Users\\super_000\\Videos\\Planetside2\\PS2Video_0009.avi")

	# Upload smaller file
	print("Uploading Test 2...")
	# Override chunk settings so we don't have a long upload
	stream.set_chunk_size(1)
	chunk_list, shredder_data = stream.upload("E:\\Users\\super_000\\Videos\\Planetside2\\PS2Video_0009.avi")

	return chunk_list, shredder_data

def unit_test_download(stream, chunk_list, shredder_data):
	stream.download(chunk_list, shredder_data)


if __name__ == "__main__":
	try:
		stream = Streamer("http://node1.storj.io")
		unit_test_upload_chunk(stream)
		unit_test_download_chunk(stream)
		chunk_list,shredder_data = unit_test_upload(stream)
		unit_test_download(stream, chunk_list, shredder_data)
	except AssertionError:
		print("Testing Failed...")
	else:
		print("Testing Passed...")