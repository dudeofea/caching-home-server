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
				return nativeImage[prop] = "/cache/" + domain + value;
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
	s.src = "/cache/" + domain + s.src.replace(/.*\/\/[^\/]*/, '');
	el.parentNode.replaceChild(s, el);
});
