import json
import requests
import argparse
import urllib.request


class Upstream:
	def __init__(self, server):
		"""For uploading and downloading files from Metadisk."""
		self.server = server # TODO: Check server connection


	# Upload Section
	def upload(self, path, output="uri"):
		"""
		Uploads a file via POST to the specified node. 

		Params:
		path -- The path to the file you want to upload. 

		"""
		# Open the file and upload it
		files = {'file': open(path, 'rb')}
		url = self.server + "/api/upload" # web-core API
		r = requests.post(url, files=files)
		# make sure that the url is actually valid
		if r.status_code == 404: raise LookupError
		else:
			# everthing checked out, select format
			# and then return it 
			if output == "json": return r.text
			elif output == "uri": return self.parse_uri(r.text)
			else: return self.parse_tuple(r.text)

	def parse_uri(self, raw):
		"""
		Takes the raw JSON from an upload request and turns in to a URI
		that we can directly use in Metadisk.

		Params:
		raw -- JSON data from upload()
		"""
		data = json.loads(raw)
		return data['filehash'] + "?key=" + data['key']

	def parse_tuple(self, raw):
		"""
		Takes the raw JSON from an upload request and turns in to a tuple so
		we can use in our application.

		Params:
		raw -- JSON data from upload()
		"""

		data = json.loads(raw)
		return (data['filehash'], data['key'])

	# Download Section
	def download(self, filehash, destination, decryptkey = ""):
		"""
		Download the file via GET from the specified node.

		Params:
		filehash -- The hash of the file that we are trying to download.
		destination -- Path where we store the file. 
		decryptkey(optional) -- The decryption key of the file we are trying to download.

		"""
		return urllib.request.urlretrieve("http://google.com", "files/" + filehash)


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
	parser = argparse.ArgumentParser()

	# Add Arguments
	parser.add_argument('action')
	parser.add_argument('-s', '--server', default="http://node1.storj.io")
	parser.add_argument('-f', '--filepath')
	args = parser.parse_args()
	
	# Do Commands
	up = Upstream("http://node1.storj.io")
	if args.action == "upload":
		result = up.upload(args.filepath, "uri")
		print(result)
	elif args.action == "download":
		filehash = "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
		decryptkey = "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c"
		result = up.download(filehash, decryptkey)
		print(result)

	#result = upload("http://node1.storj.io/api/upload", "test.txt")
	#uri = parse_uri(result)
	#print(uri)