from flask import Flask, send_file, request
from bs4 import BeautifulSoup
import urllib2
import re
import os

app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello World!"

@app.route('/view/<path:subpath>')
def view_page(subpath):
	response = dlurl(subpath)
	html = response.read()
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
	return str(soup)

@app.route('/cache/<path:subpath>')
def check_cache(subpath):
	local_path = "cache/" + os.path.basename(subpath)
	#useful later on
	if not os.path.exists(local_path):
		folders = "/".join(local_path.split("/")[:-1])
		if not os.path.exists(folders):
			os.makedirs(folders)
	#download the file and serve
	dlfile(subpath, local_path)
	print "serving: " + local_path
	return send_file(local_path)

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
