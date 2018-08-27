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
				return nativeImage[prop] = value;
			},
			get: function(target, prop) {
				return target[prop];
			}
		};
		return new Proxy(nativeImage, handler);
	}
}
Image = FakeImage;
