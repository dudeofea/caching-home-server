import re

#take a url, and return one that points it to the cache
def cacheUrl(url, domain):
	#remove bogus stuff
	if url == "" or url == None or domain == "" or domain == None:
		return None
	#if url starts with //, replace with http://
	if re.match(r"\/\/", url):
		url = url.replace("//", "http://")
	#detect if url has a domain
	if re.search(r"https?:\/\/", url):
		absolute = url;
	else:
		absolute = domain + url;
	#remove duplicate slashes from url
	return "/cache/" + re.sub(r"([^:]\/)\/+", r"\1", absolute)
