var util = require("./util");
var schedule;
var noAsyncScheduler = () => {
	throw new Error(
		"No async scheduler available\u000a\u000a    See http://goo.gl/MqrFmX\u000a",
	);
};
var NativePromise = util.getNativePromise();
if (util.isNode && typeof MutationObserver === "undefined") {
	var GlobalSetImmediate = global.setImmediate;
	var ProcessNextTick = process.nextTick;
	schedule = util.isRecentNode
		? (fn) => {
				GlobalSetImmediate.call(global, fn);
			}
		: (fn) => {
				ProcessNextTick.call(process, fn);
			};
} else if (
	typeof NativePromise === "function" &&
	typeof NativePromise.resolve === "function"
) {
	var nativePromise = NativePromise.resolve();
	schedule = (fn) => {
		nativePromise.then(fn);
	};
} else if (
	typeof MutationObserver !== "undefined" &&
	!(
		typeof window !== "undefined" &&
		window.navigator &&
		(window.navigator.standalone || window.cordova)
	) &&
	"classList" in document.documentElement
) {
	schedule = (() => {
		var div = document.createElement("div");
		var opts = { attributes: true };
		var toggleScheduled = false;
		var div2 = document.createElement("div");
		var o2 = new MutationObserver(() => {
			div.classList.toggle("foo");
			toggleScheduled = false;
		});
		o2.observe(div2, opts);

		var scheduleToggle = () => {
			if (toggleScheduled) return;
			toggleScheduled = true;
			div2.classList.toggle("foo");
		};

		return function schedule(fn) {
			var o = new MutationObserver(() => {
				o.disconnect();
				fn();
			});
			o.observe(div, opts);
			scheduleToggle();
		};
	})();
} else if (typeof setImmediate !== "undefined") {
	schedule = (fn) => {
		setImmediate(fn);
	};
} else if (typeof setTimeout !== "undefined") {
	schedule = (fn) => {
		setTimeout(fn, 0);
	};
} else {
	schedule = noAsyncScheduler;
}
module.exports = schedule;
