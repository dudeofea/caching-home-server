//Run tests with `npm test`
var assert = require('assert'),
	rewire = require('rewire'),
	MockBrowser = require('mock-browser').mocks.MockBrowser,
	jsdom = new MockBrowser();

document = jsdom.getDocument(),
document.__ENV__ = "testing",
windowmock = jsdom.getWindow();
window = {
	location: {
		host: "localpath:1000"
	}
};
Image = windowmock.Image;
injected = rewire("./injected.js");

function setDomain(d){
	injected.__set__("domain", d);
	return d;
}

describe('Tent Router', function() {
	var cacheUrl = injected.__get__("cacheUrl");

	it('[cacheUrl] Should start with /cache/<domain>/', function() {
		var domain = setDomain("www.thisisthedomain.com");
		var url = cacheUrl("/hey");
		assert.equal("/cache/"+domain+"/hey", url);
	});
	it('[cacheUrl] Should remove additional slashes', function() {
		var domain = setDomain("www.thisisthedomain.com/");
		var url = cacheUrl("//hey");
		assert.equal("/cache/www.thisisthedomain.com/hey", url);
	});
	it('[cacheUrl] Ignores bogus input arguments', function() {
		assert.equal(null, cacheUrl(function(){ return ""; }));
		assert.equal(null, cacheUrl(null));
		assert.equal(null, cacheUrl(""));
	});
	it('[cacheUrl] Should not use given domain if already exists (except localhost)', function() {
		setDomain("www.thisisthedomain.com");
		var domain = "https://www.thisisthecorrectdomain.com";
		var url = cacheUrl(domain+"/hey");
		assert.equal("/cache/"+domain+"/hey", url);
		domain = "http://www.thisisthecorrectdomain.com";
		url = cacheUrl(domain+"/hey");
		assert.equal("/cache/"+domain+"/hey", url);
		//except with localhost, we don't count that
		url = cacheUrl("http://"+window.location.host+"/hey");
		assert.equal("/cache/www.thisisthedomain.com/hey", url);
		url = cacheUrl("https://"+window.location.host+"/hey");
		assert.equal("/cache/www.thisisthedomain.com/hey", url);
	});
});
