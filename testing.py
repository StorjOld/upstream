from Upstream import Upstream

# Connect to server 
up = Upstream("http://node1.storj.io")

# Upload file
chunk = up.upload("C:\\Users\\super3\\Code\\upstream\\test.txt")
assert(chunk.filehash == "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac")
assert(chunk.decryptkey == "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c")

# Download file back
up.download(chunk)

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