import json
import requests
import argparse
import urllib.request
from urllib.parse import urlsplit

from Chunk import Chunk


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
			filehash -- The hash of the file that we are trying to download.
			destination -- Path where we store the file. 
			decryptkey(optional) -- The decryption key of the file we are 
			trying to download.

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


# UGH
def upload_command():
	try:
		result = upload(args.server, args.filepath)
		uri = parse_uri(result)
	except FileNotFoundError:
		print("File not found.")
	except TypeError:
		print("File not found.")
	except LookupError:
		print("Error connecting to server.")
	else:
		print(uri)

if __name__=="__main__":
	# Start ArgParse
	# Ok most of this ArgParse stuff is pretty bad, don't 
	# know enough about it to use it properly
	parser = argparse.ArgumentParser()

	# Add Arguments
	parser.add_argument('action')
	parser.add_argument('-s', '--server', default="http://node1.storj.io")
	parser.add_argument('-f', '--filepath')
	parser.add_argument('-u', '--uri')
	args = parser.parse_args()
	
	# Do Commands
	up = Upstream("http://node1.storj.io")
	if args.action == "upload":
		result = up.upload(args.filepath, "uri")
		print(result)
	elif args.action == "download":
		filehash, decryptkey = up.decode_uri(args.uri)
		result = up.download(filehash, decryptkey)
		print(result)