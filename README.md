upstream
========

[![Build Status](https://drone.io/github.com/angstwad/upstream/status.png)](https://drone.io/github.com/angstwad/upstream/latest)

Command line tool for uploading and downloading files from Metadisk and web-core.

## Chunk Class
The chunk class is for stores information about an encrypted chunk, including its hash and decryption key. This allows us to be able to covert between various formats needed in this tool and [Metadisk](https://github.com/storj/metadisk). 

### Example Usage 
```
cryptkey = "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c"
filehash = "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
full_chunk = Chunk(filehash, cryptkey)
print full_chunk.get_json()
```

```
{  
   "key":"2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c",
   "filehash":"5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
}
```

### Full Spec

TODO

## Streamer Class
These are the transfer functions that are used to upload and download raw data to/from a node.

### Upload Usage
```
streamer = Streamer('http://node1.metadisk.org')
chunk = streamer.upload(path)
```

### Upload Example
File is uploaded via a POST request to the [Metadisk](http://metadisk.org) node via its [web-core](https://github.com/Storj/web-core#api-documentation) API. There is currently a node running [here](http://node1.storj.io). Currently our default chunk size is 32 MB.

	up = Upstream("http://node1.storj.io")
	chunk = up.upload("C:\\Users\\super3\\Code\\upstream\\test.txt")

### Download Usage

```
result = streamer.download(chunk, destination)
```

### Download Example

```	
streamer = Streamer("http://node1.storj.io")
filehash = "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
decryptkey = "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c"
chunk = Chunk(filehash, decryptkey)
result = streamer.download(chunk, destination)
```

### Full Spec

TODO

