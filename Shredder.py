import os

class Shredder:
	def __init__(self, filepath, chunk):
		"""For shreding and merging larger files to be uploaded."""
		self.filepath = filepath
		self.filename = os.path.split(filepath)[1]

		self.chunk_names = []
		self.chunk_size = chunk
		self.num_chunks = 0

	def shred_chunks(self):
		"""
		Split the file into smaller chunks.
		http://bdurblg.blogspot.com/2011/06/python-split-any-file-binary-to.html

		"""
		# read the contents of the file
		f = open(self.filepath, 'rb')
		data = f.read() # read the entire content of the file(MEMORY!)
		f.close()

		# get the length of data, ie size of the input file in bytes
		bytes = len(data)

		# calculate the number of chunks to be created
		self.num_chunks = bytes/self.chunk_size
		if(bytes%self.chunk_size):
			self.num_chunks+=1

		# create chunks
		for i in range(0, bytes+1, self.chunk_size):
			fn1 = "upload/chunk%s" % i  
			print(fn1)
			self.chunk_names.append(fn1)
			f = open(fn1, 'wb')
			f.write(data[i:i+ self.chunk_size])
			f.close()

		return self.chunk_names

	def merge_chunks(self):
		"""
		Join the chunks of files into a single file.
		http://bdurblg.blogspot.com/2011/06/python-split-any-file-binary-to.html

		"""

		dataList = []

		for i in range(0,int(self.num_chunks),1):
			chunkNum=i * self.chunk_size
			chunkName = os.path.abspath('download/chunk%s'%chunkNum)
			print(chunkNum)
			print(chunkName)
			f = open(chunkName, 'rb')
			dataList.append(f.read())
			f.close()
			os.remove(chunkName)
		
		if os.path.exists("files/" + self.filename):
			os.remove("files/" + self.filename)
		for data in dataList:
			f = open("files/" + self.filename, 'ab')
			f.write(data)
			f.close()