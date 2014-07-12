upstream
========

Command line tool for upload and downloading files from Metadisk.

## Raw Functions
These are the raw functions that are used to upload and download raw data to/from a node. These should be called by the application or other functions rather than being used directly. They don't encrypt the data, or account for file size limits.

### Upload Usage
File is uploaded via a POST request to the [Metadisk](http://metadisk.org) node via its [web-core](https://github.com/Storj/web-core#api-documentation) API. There is currently a node running [here](https://github.com/Storj/web-core#api-documentation).

	upstream.py upload -s <node url> -f <file path>

### Upload Example

	upstream.py -f "C:\test.txt"

### Upload Result
The upload should return the hash for the file, as well the decryption key in URI format. 

	5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac?key=2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c

Possible errors:

- "File not found."
- "Error connecting to server."

## Helper Functions
Designed to solve a few Metadisk integration problems.

### parse_uri

Takes the raw JSON from an uplaod request and turns in to a URI	that we can directly use in Metadisk. So it turns this:

	{
		"filehash": "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac",
		"key": "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c"
	}

into this:

	5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac?key=2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c