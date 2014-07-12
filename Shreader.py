from Upstream import Upstream

class Shreader:
	def __init__(self, filepath, chunk = 32):
		"""For shreading and merging larger files to be uploaded."""
		self.filepath = filepath
		self.chunk = 32 # MB

	def shread(self):
		"""
		Splits up a larger file to a specified chunk size, and uploads each peice.
		If the file is smaller than the chunks size the file will be uploaded like normal.
		Returns us a JSON list of the filenames, hashes, and decryption keys.
		"""
		pass

	# Merge Section
	def merge(self, fragments):
		"""
		Takes a JSON file with our file fragments locations and merges them all back 
		into one file.

		Params:
		fragments -- JSON file from shread()
		"""
		pass