from flask import Flask, send_file
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
	response = urllib2.urlopen(subpath)
	html = response.read()
	#print html
	soup = BeautifulSoup(html)
	for link in soup.findAll('img'):
		link['src'] = "/cache/"+subpath+"/"+link['src']
	#inject js up top in <head>
	script = soup.new_tag("script")
	with open("injected.js") as f:
		script.string = f.read()
	soup.head.insert(0, script)
	return str(soup)

@app.route('/cache/<path:subpath>')
def check_cache(subpath):
	local_path = os.path.basename(subpath)
	dlfile(subpath, local_path)
	print "serving: " + local_path
	return send_file(local_path)

def dlfile(url, path):
	# Open the url
	f = urllib2.urlopen(url)
	print "downloading " + url
	# Open our local file for writing
	with open(path, "wb") as local_file:
		local_file.write(f.read())
