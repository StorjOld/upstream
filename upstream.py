import json
import requests
import argparse
import urllib.request
from urllib.parse import urlsplit

from Chunk import Chunk
from Shreader import Shreader


class Upstream:
	def __init__(self, server):
		"""
		For uploading and downloading files from Metadisk.

		Params:
			server -- URL to the Metadisk server.

		"""
		self.server = server
		self.check_connectivity()

	def check_connectivity(self):
		"""
		Check to see if we even get a connection to the server. 
		https://stackoverflow.com/questions/3764291/checking-network-connection

		"""
		try:
			urllib.request.urlopen(self.server, timeout=1)
		except urllib.request.URLError:
			raise LookupError("Could not connect to server.")

	# Upload Section
	def upload(self, path):
		"""
		Uploads a file via POST to the specified node. 
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


	# Download Section
	def download(self, chunk, destination=""):
		"""
		Download the file via GET from the specified node.
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
def unit_test_upload():
	# Connect to server 
	up = Upstream("http://node1.storj.io")

	# Upload file and check file
	chunk = up.upload("C:\\Users\\super3\\Code\\upstream\\test.txt")
	assert(chunk.filehash == "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac")
	assert(chunk.decryptkey == "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c")

	# Connect to wrong server
	try:
		up = Upstream("http://blah.storj.io")
	except LookupError:
		assert(True)
	else:
		assert(False)

	# Try to upload wrong file
	try:
		chunk = up.upload("blah")
	except FileNotFoundError:
		assert(True)
	else:
		assert(False)

def unit_test_download():
	# Connect to server
	up = Upstream("http://node1.storj.io")

	# Make chunk
	filehash = "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
	decryptkey = "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c"
	get_chunk = Chunk(filehash, decryptkey)

	# Download Chunk
	up.download(get_chunk, "C:\\Users\\super3\\Code\\upstream\\files\\test.txt")


if __name__ == "__main__":
	try:
		unit_test_upload()
		unit_test_download()
	except AssertionError:
		print("Testing Failed...")
	else:
		print("Testing Passed...")