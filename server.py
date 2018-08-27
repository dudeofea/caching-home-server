from flask import Flask, send_file, request
from bs4 import BeautifulSoup
import urllib2
import urlparse
import re
import os

app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello World!"

@app.route('/view/<path:subpath>')
def view_page(subpath):
	htmlfile, found = _check_cache(subpath, False)
	with open(htmlfile, 'r') as myfile:
		html = myfile.read()
	if found:
		return html
	#redirect css url() links to cache
	html = re.sub(r'url\(([^\)]*)\)', lambda m: "url(/cache/" + str(subpath) + m.group(1) + ")", html)
	soup = BeautifulSoup(html, "lxml")
	#redirect image links to cache
	for link in soup.findAll('img'):
		src = link.get('src')
		if src:
			link['src'] = "/cache/"+subpath+"/"+src
		srcset = link.get('srcset')
		if srcset:
			links = link['srcset'].split(",")
			new = []
			for l in links:
				l = l.strip()
				split = l.split(" ")
				split[0] = "/cache/"+subpath+"/"+split[0]
				new.append(" ".join(split))
			link['srcset'] = ", ".join(new)
	#redirect script links to cache
	for link in soup.findAll('script'):
		if 'src' in link:
			link['src'] = "/cache/"+subpath+"/"+link['src']
	#inject js up top in <head>
	script = soup.new_tag("script")
	with open("injected.js") as f:
		script.string = f.read()
	soup.head.insert(0, script)
	#write file to cache
	with open(htmlfile, 'w') as myfile:
		myfile.write(str(soup))
	return str(soup)

@app.route('/cache/<path:subpath>')
def check_cache(subpath):
	local_path, _ = _check_cache(subpath, False)
	return send_file(local_path)

def _check_cache(subpath, purge):
	#parse the url
	parsed = urlparse.urlparse(subpath)
	print "subpath: ", parsed
	if parsed.path != "/" and parsed.path != "":
		local_path = "cache/" + parsed.netloc + parsed.path
	else:
		local_path = "cache/" + parsed.netloc + "/index"
	#check if it's in the cache
	found = True
	if not os.path.exists(local_path):
		folders = "/".join(local_path.split("/")[:-1])
		if not os.path.exists(folders):
			os.makedirs(folders)
		#download the file and serve
		dlfile(subpath, local_path)
		found = False
	print "serving: " + local_path
	return local_path, found

def dlfile(url, path):
	# Open the url
	f = dlurl(url)
	print "downloading " + url
	# Open our local file for writing
	with open(path, "wb") as local_file:
		local_file.write(f.read())

def dlurl(url):
	ua = request.headers.get('User-Agent')
	req = urllib2.build_opener()
	req.addheaders = [('User-Agent', ua)]
	return req.open(url)
