import argparse
from Chunk import Chunk
from Streamer import Streamer

# Parser Object
parser = argparse.ArgumentParser()

# Add Arguments
parser.add_argument('action')
parser.add_argument('-s', '--server', default="http://node1.storj.io")
parser.add_argument('-f', '--filepath')
parser.add_argument('-u', '--uri')
parser.add_argument('-d', '--destination')

# Get Args
args = parser.parse_args()

# Do Commands
stream = Streamer("http://node1.storj.io")
if args.action == "upload":
	chunk_list, shredder_data = stream.upload(args.filepath)
elif args.action == "download":
	chunk = [Chunk().load_uri(args.uri)]
	if args.destination == "": result = stream.download(chunk)
	else: result = stream.download(chunk, None, args.destination)
elif args.action == "file":
	pass
