from Upstream import Upstream

# Connect to Server 
up = Upstream("http://node1.storj.io")

# Upload Unit Testing
result = up.upload("text.txt", "uri")
print(result)
uri = parse_uri(result)
print(uri)