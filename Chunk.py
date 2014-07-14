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