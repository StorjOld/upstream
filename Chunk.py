import json

class Chunk:
	def __init__(self, filehash = "", decryptkey = ""):
		"""
		Stores information about an encryted chunk. Allows for
		format conversions. 

		Params:
			filehash -- The hash for a file.
			decryptkey -- The decryption key for a file.

		"""
		self.filehash = filehash
		self.decryptkey = decryptkey

	# Loads
	def load_uri(self, raw):
		self.filehash, self.decryptkey = str(raw).split("?key=")
		return self

	def load_json(self, raw):
		self.raw_json = raw
		data = json.loads(raw)
		self.filehash = data['filehash'] 
		self.decryptkey = data['key']
		return self

	# Gets
	def get_uri(self):
		return self.filehash + "?key=" + self.decryptkey

	def get_tuple(self):
		return (self.filehash, self.decryptkey)

	def get_json(self):
		return json.dumps({"filehash": self.filehash, "key":  self.decryptkey})


# Unit Testing
def run_gets(chunk):
	chunk.get_uri()
	chunk.get_tuple()
	chunk.get_json()

def unit_test():
	# Some values
	filehash = "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
	decryptkey = "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c"

	# Create empty object
	empty_chunk = Chunk()
	# Create half object
	half_chunk = Chunk(filehash)
	# Create full object
	full_chunk = Chunk(filehash, decryptkey)

	# Run getters 
	run_gets(empty_chunk)
	run_gets(half_chunk)
	run_gets(full_chunk)

	# Create new objects
	chunk1 = Chunk()
	chunk2 = Chunk()

	# Load content
	raw_json = """
	{ 
		"key": "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c",
		"filehash": "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
	}
	"""
	chunk1.load_json(raw_json)
	raw_uri = "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac?key=2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c"
	chunk2.load_uri(raw_uri)

	# Fit everything into one test case
	assert(chunk1.get_tuple()==chunk2.get_tuple())
	print(full_chunk.get_json())


if __name__ == "__main__":
	try:
		unit_test()
	except AssertionError:
		print("Testing Failed...")
	else:
		print("Testing Passed...")