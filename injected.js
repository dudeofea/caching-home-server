var domain = "https://www.google.com/";
//For catching "new Image().src =" calls
const NativeImage = Image;
class FakeImage {
	constructor(w, h) {
		const nativeImage = new NativeImage(w, h);
		const handler = {
			set: function(obj, prop, value) {
				if (prop === 'src') {
					console.log('gotcha ' + value);
				}
				return nativeImage[prop] = cacheUrl(value);
			},
			get: function(target, prop) {
				return target[prop];
			}
		};
		return new Proxy(nativeImage, handler);
	}
}
Image = FakeImage;

//For catching js injected scripts
var createElement = document.createElement;
document.createElement = function (tag) {
	if (tag === 'script') {
		tag = 'custom:script';
	}
	return createElement.call(document, tag);
};
document.addEventListener('DOMNodeInserted', function (event) {
	var el = event.target;
	if (el.nodeName !== 'CUSTOM:SCRIPT') {
		return;
	}
	//create a new (real script) tag with a modified url
	var s = createElement.call(document, "script");
	for (var attr in el) {
		if (el.hasOwnProperty(attr)) {
			s[attr] = el[attr];
		}
	}
	s.src = cacheUrl(s.src);
	el.parentNode.replaceChild(s, el);
});

//function for changing the domain of something to our cache
function cacheUrl(url){
	//remove bogus shit
	if(url === null || typeof url !== "string" || url === ""){
		return;
	}
	//remove local domain if we find one
	var ind = url.indexOf(window.location.host);
	if(ind > -1){
		url = url.substring(ind+window.location.host.length);
	}
	//detect if url has a domain
	var absolute;
	if (url.match(/https?:\/\//g)) {
		absolute = url;
	}else{
		absolute = domain + url;
	}
	//remove extra slashes and return
	return "/cache/" + absolute.replace(/([^:]\/)\/+/g, "$1");
};
