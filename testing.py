from Upstream import Upstream

# Connect to server 
up = Upstream("http://node1.storj.io")

# Upload file
chunk = up.upload("C:\\Users\\super3\\Code\\upstream\\test.txt")
assert(chunk.filehash == "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac")
assert(chunk.decryptkey == "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c")

# Download file back
up.download(chunk)