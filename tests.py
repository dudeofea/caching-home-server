import unittest
from tools import cacheUrl

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

if __name__ == '__main__':
	unittest.main()
