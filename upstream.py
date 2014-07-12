import json
import requests
import argparse


def upload(url, path):
	"""
	Uploads a file via POST to the specified node. 

	Params:
	url -- The API url of the node. 
	path -- The path to the file you want to upload. 

	"""
	# Open the file and upload it
	files = {'file': open(path, 'rb')}
	r = requests.post(url, files=files)
	# make sure that the url is actually valid
	if r.status_code == 404:
		raise LookupError
	else:
		# everthing checked out, print json
		return r.text


def parse_uri(raw):
	"""
	Takes the raw JSON from an uplaod request and turns in to a URI
	that we can directly use in Metadisk.
	"""
	data = json.loads(raw)
	return data['filehash'] + "?key=" + data['key']

def upload_command():
	try:
		result = upload(args.server + "/api/upload", args.filepath)
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
	
	# Do Upload
	if args.action == "upload":
		upload_command()
	elif args.action == "uploadm":
		pass

	#result = upload("http://node1.storj.io/api/upload", "test.txt")
	#uri = parse_uri(result)
	#print(uri)