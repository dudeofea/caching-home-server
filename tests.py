import unittest
import docker
import urllib2
import time
import json
from tools import cacheUrl

client = docker.from_env()

class TestCacheUrl(unittest.TestCase):

	#starts with /cache
	def test_cacheUrl_starts_with_cache(self):
		domain = "www.thisisthedomain.com"
		self.assertEqual(cacheUrl("/hey", domain), "/cache/"+domain+"/hey")

	def test_cacheUrl_removes_extra_slashes(self):
		domain = "www.thisisthedomain.com//"
		self.assertEqual(cacheUrl("/hey//", domain), "/cache/www.thisisthedomain.com/hey/")

	def test_cacheUrl_ignores_bogus_input(self):
		self.assertEqual(cacheUrl("", ""), None)
		self.assertEqual(cacheUrl("some_url", ""), None)
		self.assertEqual(cacheUrl(None, None), None)
		self.assertEqual(cacheUrl(None, "www.adomain.org"), None)
		self.assertEqual(cacheUrl("some_url", None), None)

	#test that urls with defined domains are cached with that domain
	#and not <current domain>/<defined domain>
	def test_cacheUrl_uses_existing_domain(self):
		bad_domain = "www.thisisthedomain.com"
		good_domain = "https://www.thisisthecorrectdomain.com"
		self.assertEqual(cacheUrl(good_domain+"/hey", bad_domain), "/cache/"+good_domain+"/hey")
		good_domain = "http://www.thisisthecorrectdomain.com"
		self.assertEqual(cacheUrl(good_domain+"/hey", bad_domain), "/cache/"+good_domain+"/hey")
		good_domain = "//www.thisisthecorrectdomain.com";
		url = cacheUrl(good_domain+"/hey", bad_domain);
		self.assertEqual(url, "/cache/http://www.thisisthecorrectdomain.com/hey")

class IntegrationTests(unittest.TestCase):
	splash_container = None

	@classmethod
	def setUpClass(cls):
		cls.splash_container = client.containers.run("scrapinghub/splash", detach=True, ports={'8050/tcp':8050, '5023/tcp':5023})
		time.sleep(0.5)

	@classmethod
	def tearDownClass(cls):
		print "hey", cls.splash_container
		cls.splash_container.kill()

	#Query Splash API for network requests
	def render_har(self, args):
		req = urllib2.build_opener()
		response = req.open("http://localhost:8050/render.har?"+args)
		return json.loads(response.read())

	def test_some_thing(self):
		har = self.render_har("url=https://www.google.com/")
		for e in har['log']['entries']:
			print(json.dumps(e['request']['url'], indent=4, sort_keys=True))

if __name__ == '__main__':
	unittest.main()
