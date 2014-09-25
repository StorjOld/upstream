upstream
========

[![Build Status](https://drone.io/github.com/Storj/upstream/status.png)](https://drone.io/github.com/Storj/upstream/latest)

Command line tool for uploading and downloading files from Metadisk and web-core.

## CLI

```
$ upstream --help
usage: Upstream [-h] [--server SERVER] [-v] [--version] {upload,download} ...

Command line client for the Storj web-core API

positional arguments:
  {upload,download}
    upload           Upload a file from API
    download         Download a file from API

optional arguments:
  -h, --help         show this help message and exit
  --server SERVER    Metadisk node to connect to
  -v                 Verbose output
  --version          Display version.
```

### Upload
```
$ upstream upload --help
usage: Upstream upload [-h] [--shard-size SHARD_SIZE] file

positional arguments:
  file                  Path to file to upload

optional arguments:
  -h, --help            show this help message and exit
  --shard-size SHARD_SIZE
                        Size of shards to break file into and to upload, max:
                        250m, default: 250m. Ex. 25m - file will be broken
                        into 25 MB shards and uploaded shard by shard
```

```  
$ upstream upload /path/to/file
```

```
 $ upstream upload --shard-size 3m 10megs.bin
Uploading Shard: 100% |##############################| Time: 00:00:06 523.98 K/s
Uploading Shard: 100% |##############################| Time: 00:00:08 369.53 K/s
Uploading Shard: 100% |##############################| Time: 00:00:06 472.13 K/s
Uploading Shard: 100% |##############################| Time: 00:00:01 535.82 K/s

Download this file by using the following command:
upstream download --uri 05034bfffb47a5d0e810b9666a9832cb97f78525ad7979dc496a45f67a72ce1c?key=ae01ecea6e3fa80e720fac87440f53117c0850bf47cfe9fd39511f97c03909e9 4caea2ba18c169da600a33fd9a8b87e9ccc155d1a73cb0fa113685df174f0b94?key=ff8781fcf1395ab71ffb87441471534ec0ec4622ca16a1569923712c8b859869 d01741eabd6ee29980a45ac32e42ff9dfc4d60b65446bf6b86b5efabbd8d9684?key=d87aa3ba0ebe82c66894f9cd44625f259953636dd1eb9c2d803578b954e144cd 520ee9d093943fb266908a3df006fae1ec6115551d835fdf7fdb3dc93b188f0e?key=752cc57f077c49667c3e092ece451c53a4f6790e9d3fe6f448b079acf91ed030 --dest <filename>
```

### Download
```
$ upstream download --help
usage: Upstream download [-h] --uri URI [URI ...] [--dest DEST]
                         [--shard-size SHARD_SIZE]

optional arguments:
  -h, --help            show this help message and exit
  --uri URI [URI ...]   URI, or URIs, of file to download. Accepts multiple
                        values, space separated. If multiple URIs are
                        specified, the URIs are joined to create a single file
  --dest DEST           Folder or file to download file
  --shard-size SHARD_SIZE
```

```
$ upstream download --uri <big long uri here> --dest /path/to/file

$ upstream download --uri 05034bfffb47a5d0e810b9666a9832cb97f78525ad7979dc496a45f67a72ce1c?key=ae01ecea6e3fa80e720fac87440f53117c0850bf47cfe9fd39511f97c03909e9 4caea2ba18c169da600a33fd9a8b87e9ccc155d1a73cb0fa113685df174f0b94?key=ff8781fcf1395ab71ffb87441471534ec0ec4622ca16a1569923712c8b859869 d01741eabd6ee29980a45ac32e42ff9dfc4d60b65446bf6b86b5efabbd8d9684?key=d87aa3ba0ebe82c66894f9cd44625f259953636dd1eb9c2d803578b954e144cd 520ee9d093943fb266908a3df006fae1ec6115551d835fdf7fdb3dc93b188f0e?key=752cc57f077c49667c3e092ece451c53a4f6790e9d3fe6f448b079acf91ed030 --dest my-downloaded-file-10megs.bin
Downloading file 1...
Downloading file 2...
Downloading file 3...
Downloading file 4...

Downloaded to my-downloaded-file-10megs.bin.
```

**And it works...**

```
$ shasum 10megs.bin my-downloaded-file-10megs.bin
1ed47c6d1061f18bfae227713bedd10956744fd4  10megs.bin
1ed47c6d1061f18bfae227713bedd10956744fd4  my-downloaded-file-10megs.bin

```
## Shard Class
The shard class is for stores information about an encrypted shard, including its hash and decryption key. This allows us to be able to covert between various formats needed in this tool and [Metadisk](https://github.com/storj/metadisk). 

### Example Usage 
```
cryptkey = "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c"
filehash = "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
full_shard = shard(filehash, cryptkey)
print full_shard.get_json()
```

```
{  
   "key":"2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c",
   "filehash":"5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
}
```

### Full Spec

Documented in docstrings, Sphinx compatible.

## Streamer Class
These are the transfer functions that are used to upload and download raw data to/from a node.

### Upload Usage
```
streamer = Streamer('http://node1.metadisk.org')
shard = streamer.upload(path)
```

### Upload Example
File is uploaded via a POST request to the [Metadisk](http://metadisk.org) node via its [web-core](https://github.com/Storj/web-core#api-documentation) API. There is currently a node running [here](http://node1.storj.io). Currently our default shard size is 32 MB.

	up = Upstream("http://node1.metadisk.org")
	shard = up.upload("C:\\Users\\super3\\Code\\upstream\\test.txt")

### Download Usage

```
result = streamer.download(shard, destination)
```

### Download Example

```	
streamer = Streamer("http://node1.metadisk.org")
filehash = "5547a152337de9ff6a97f6f099bb024e08af419cee613b18da76a33e581d49ac"
decryptkey = "2b77e64156f9f7eb16d74b98f70417e4d665d977d0ef00e793d41767acf13e8c"
shard = shard(filehash, decryptkey)
result = streamer.download(shard, destination)
```

### Full Spec

Documented in docstrings, Sphinx compatible.

