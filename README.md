upstream
========

Command line tool for upload and downloading files from Metadisk.

## Raw Functions
These are the raw functions that are used to upload and download raw data to/from a node. These should be called by the application or other functions rather than being used directly. They don't encrypt the data, or account for file size limits.

### Upload Usage
File is uploaded via a POST request to the [Metadisk](http://metadisk.org) node via its [web-core](https://github.com/Storj/web-core#api-documentation) API. There is currently a node running [here](https://github.com/Storj/web-core#api-documentation).

	upstream.py upload <node url> <file path>

### Upload Example

	upstream.py upload http://node1.storj.io/api/upload test.txt

### Upload Result
The upload should return the hash for the file, as well the decryption key for the file. Error codes can be returned as well.  

	3f4b75fa18684587e62c834ae6cc46c9fdad496f3583530e6adc1c9634c7b57c?key=c06b216c70f1e1b2b4ba85c907e32307c732ce0b8594bd12771aa425271bc2b7
