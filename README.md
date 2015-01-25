#Upstream

[![Build Status](https://travis-ci.org/Storj/upstream.svg)](https://travis-ci.org/Storj/upstream) [![Coverage Status](https://img.shields.io/coveralls/Storj/upstream.svg)](https://coveralls.io/r/Storj/upstream)

Upstream is a command line tool for uploading and downloading files from MetaDisk Nodes, Verification Nodes and DriveShare Farmers on the Storj network.

**NOTE**: This software is currently designed for testing purposes only. Do not use in production environments with sensitive files.

## Dependencies

Upstream (roundtrip) uses the [storjtorrent](https://github.com/storj/storjtorrent) library, which requires that libtorrent and its python bindings 
are properly installed. 


## CLI

```
$ upstream --help
usage: Upstream [-h] [--server SERVER] [-v] [--version] {upload,download,seed,retrieve} ...

Command line client to transmit and receive file data from MetaDisk and the Storj network.

positional arguments:
  {upload,download,seed,retrieve}
    upload           Upload a file using the MetaDisk API
    download         Download a file using the MetaDisk API
    seed             Seed the shards for a specified file
    retrieve         Retrieve and reconstitute shards for a given file from farmers

optional arguments:
  -h, --help         show this help message and exit
  --server SERVER    Metadisk node to connect to or verification node to notify
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

### Seed

You can use `--help` to learn how to seed your file to the Storj network.

```
$ upstream seed --help
usage: Upstream seed [-h] [--shard-size SHARD_SIZE] file

positional arguments:
  file                  File to shard and seed to network

optional arguments:
  -h, --help            show this help message and exit
  --shard-size SHARD_SIZE
                        Size of shards to break file into and to upload, max:
                        250m, default: 250m. Ex. 25m - file will be broken
                        into 25 MB shards and uploaded shard by shard
```

To seed a specific file using the default shard size:

```  
$ upstream seed /path/to/file
```

You can also specify a specific shard size for a given file:

```
 $ upstream seed --shard-size 10m 60megs.bin
```

Upon the seeding of your shards, you will see the current status of each shard. The 
example below indicates several possible status messages:

```
Transmitting Shard 1: Sending infohash to verification server...
Transmitting Shard 2: Sending infohash to verification server...
Transmitting Shard 3: Waiting for verification server to retrieve shard...
Transmitting Shard 4: Assigning shard to farmer(s)...
Transmitting Shard 5: Verifying farmer(s) receipt of shard...
Transmitting Shard 6: Ready!
```

Seeding your file will create a directory containing each encrypted shard and a corresponding
data file containing information used to retrieve and reconstruct your file.

For example, the `60megs.bin` file would have an associated `60megs.bin.info` file containing 
something similar to the following example:

```
{
  'shard_size': '10m',
  'shard_catalog': {
    '1': {
        'infohash': '9E3JAGK9B6W0DQDPF53LZZ23ZNS8QLGA',
        'filehash': 'ms4mrr9w3gc4e3uygqrbl9q8q6jx0nq8eakw4nwj9ell17xstzvo2ibj9hc73siu',
        'key': 'dbass5qentpmc4s02ty05jq5wvj0a5cuswxlh78wa5eqd47bu287gse0o6pu04qq'
    },
    '2': {
        'infohash': 'JAL94C7B83E53OEG6KOT5ANDRI131A1G',
        'filehash': '9zahf2ea5lcaszmudty5p0uvbrbdnivj9zuiijq9somrm14z3zdllmavlmg0pipf',
        'key': 'p4sd90kyyr3fxtj1565v1nh9cukzqkcwr38o12x1fpsg69r2zc0wyoq5ktoht9a7'
    },
    '3': {
        'infohash': 'GCFW2X71269654T0N2SATQAEV40CBTX1',
        'filehash': 'o5mbbt2cfmljeq8tvvi8qxii6olok1mmyjcleeecr096ksoy4n0nk42d2vflt28r',
        'key': 'l7dpyw5xwurkhuc9ddd7btuvowbwxr68pz6t2rgu16opl2cuyqs8qce6724yq3y5'
    },
    '4': {
        'infohash': '7X3JZBH7KO2B5JK60B5FF6IUG4VX7T02',
        'filehash': 'p19elgc7cmeuevpi0m8z04rvao7uc55vkcsprtmlycoujmby8fnjlu9sk56qidxq',
        'key': 'crba8bosgw8gdl9w5rrgcqx08bb8jaoq8xagn7wkzhwyhyzdq0v9mc4pm25pzthi'
    },
    '5': {
        'infohash': '4W12C4450O5MBDJCGTBP8SIWH36439CJ',
        'filehash': 'vaabiwtxo479ptjqe6nbkke97a05qwj2emgyweped92b8u9aobz130tu3kgxj8k7',
        'key': '3z354cgk85pz5ohvfnt1ir4ykueldf9vjkp53q27ku7ssghje894wbc3nekdmtw0'
    },
    '6': {
        'infohash': '0974T73WJ3SY5Z5LEZ4UYKGDMRA1RF4C',
        'filehash': '81rapt3tzusqcg5j96g15zk75cq29jjjpapo8jbw9ku9crg8xosd6ju9gkrx657r',
        'key': 'jjat1wgdoh3akwzi8pr40ta9rza36wa4gn42ocx8tvb8b8qfduvkyc6ze29zmaer'
    }
  }
}
```

When all shards have been safely received by farmers, you will be able to retrieve and 
reconstruct your file via the following command:

```
$ upstream retrieve --file 60megs.bin
````

### Retrieve

You can use `--help` to learn how to retrieve your file shards from Storj farmers.

```
$ upstream retrieve --help
usage: Upstream retrieve [-h] --file FILE [--dest DEST]

optional arguments:
  -h, --help            show this help message and exit
  --dest DEST           Folder or file to download file
```

To properly retrieve a file, a corresponding info file with shard details should have already been created.

Retrieving a file will download all composite shards from farmers, decrypt them and reconstitute them into the original file:

```

$ upstream retrieve --file 60megs.bin --dest get-my-stuff-60megs.bin
Retreiving shards...100%.
Decrypting and reconstituting shards...done!
Retrieved file saved to get-my-stuff-60megs.bin.
```

## Shard Class

The shard class stores information about an encrypted shard including its hash and decryption key. This allows us to be able to convert between various formats needed in this tool and [MetaDisk](https://github.com/storj/metadisk). 

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

File is uploaded via a POST request to the [MetaDisk](http://metadisk.org) node via its [web-core](https://github.com/Storj/web-core#api-documentation) API. There is currently a node running [here](http://node1.storj.io). Our default shard size is currently 32 MB.

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
