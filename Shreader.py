import os
from Upstream import Upstream

class Shreader:
	def __init__(self, filepath, chunk = 32):
		"""For shreading and merging larger files to be uploaded."""
		self.filepath = filepath
		self.filename = os.path.split(filepath)[1]
		print(self.filename)

		self.chunkNames = []
		self.chunkSize = chunk * 1048576 # megabytes to bytes
		self.noOfChunks = 0

		self.storjchunks = []

	def shread(self):
		"""
		Splits up a larger file to a specified chunk size, and uploads each peice.
		If the file is smaller than the chunks size the file will be uploaded like normal.
		Returns us a JSON list of the filenames, hashes, and decryption keys.
		"""

		# Split File Up
		self.splitFile()

		# Upload File
		up = Upstream("http://node1.storj.io")
		for i in self.chunkNames:
			filepath = os.path.abspath(i)
			print(filepath)
			result = up.upload(filepath, "tuple")
			os.remove(filepath)

			# filename, hash, decrypt key
			tmpchunk = (os.path.split(i)[1], result[0], result[1]) 
			self.storjchunks.append(tmpchunk)

		return self.storjchunks


	# Merge Section
	def merge(self):
		up = Upstream("http://node1.storj.io")

		for i in self.storjchunks:
			chunkname = i[0]
			filehash = i[1]
			decryptkey = i[2]
			up.download(filehash, decryptkey, "download/" + chunkname)

		self.joinFiles()

	def splitFile(self):
		"""
		Function to split the file into smaller chunks.
		From: http://bdurblg.blogspot.com/2011/06/python-split-any-file-binary-to.html

		"""
		# read the contents of the file
		f = open(self.filepath, 'rb')
		data = f.read() # read the entire content of the file
		f.close()

		# get the length of data, ie size of the input file in bytes
		bytes = len(data)

		# calculate the number of chunks to be created
		self.noOfChunks = bytes/self.chunkSize
		if(bytes%self.chunkSize):
			self.noOfChunks+=1

		# create chunks
		for i in range(0, bytes+1, self.chunkSize):
			fn1 = "upload/chunk%s" % i  
			print(fn1)
			self.chunkNames.append(fn1)
			f = open(fn1, 'wb')
			f.write(data[i:i+ self.chunkSize])
			f.close()

		#create a info.txt file for writing metadata
		#f = open('info.txt', 'w')
		#f.write(inputFile+','+'chunk,'+str(noOfChunks)+','+str(chunkSize))
		#f.close()

	def joinFiles(self):
		"""
		Join the chunks of files into a single file.
		"""

		dataList = []

		for i in range(0,int(self.noOfChunks),1):
			chunkNum=i * self.chunkSize
			chunkName = os.path.abspath('download/chunk%s'%chunkNum)
			f = open(chunkName, 'rb')
			dataList.append(f.read())
			f.close()

		
		for data in dataList:
			f = open("files/" + self.filename, 'wb')
			f.write(data)
			f.close()


if __name__ ==  "__main__":
	# call the file splitting function
	shread = Shreader("C:\\Users\\super3\\Desktop\\alive.png", 16)
	shread.shread()
	shread.merge()

	#call the function to join the splitted files
	#joinFiles('chunk',7,110000000)