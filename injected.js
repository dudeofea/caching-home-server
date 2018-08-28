var domain = "#!<DOMAIN>!#";
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

// //For catching js injected scripts
var createElement = document.createElement;
document.createElement = function (tag) {
	if (tag.toLowerCase() === 'script') {
		tag = 'custom:script';
	}
	if (tag.toLowerCase() === "img"){
		return new Image();
	}
	return createElement.call(document, tag);
};
document.addEventListener('DOMNodeInserted', function (event) {
	var el = event.target;
	if (el.nodeName !== 'CUSTOM:SCRIPT') {
		return;
	}
	var src = el.src;
	if(!el.src){
		console.log("src null", el.attributes);
		if(el.attributes && el.attributes.src){
			src = el.attributes.src.nodeValue;
		}
	}
	//console.log('gotcha ', el.outerHTML, src);
	//create a new (real script) tag with a modified url
	var s = createElement.call(document, "script");
	for (var attr in el) {
		if (el.hasOwnProperty(attr)) {
			s[attr] = el[attr];
		}
	}
	s.src = cacheUrl(src);
	//console.log('gotcha ', s.outerHTML, s.attributes);
	el.parentNode.replaceChild(s, el);
});

//for catching XHR requests
var oldXHR = window.XMLHttpRequest;
function newXHR() {
    var realXHR = new oldXHR();
    realXHR.addEventListener("readystatechange", function() {
		//console.log("xhr sent", realXHR);
        if(realXHR.readyState==4 && realXHR.status==200){
        }
    }, false);
	realXHR._open = realXHR.open;
	realXHR.open = function(method, url, asyn, user, password){
		console.log("mocking open", method, url);
		return this._open(method, cacheUrl(url), asyn, user, password);
	};
    return realXHR;
}
window.XMLHttpRequest = newXHR;

//function for changing the domain of something to our cache
function cacheUrl(url){
	//remove bogus shit
	if(url === null || typeof url !== "string" || url === ""){
		return;
	}
	//if url starts with //, replace with http://
	if(url[0] == "/" && url[1] == "/"){
		url = url.replace("//", "http://")
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
