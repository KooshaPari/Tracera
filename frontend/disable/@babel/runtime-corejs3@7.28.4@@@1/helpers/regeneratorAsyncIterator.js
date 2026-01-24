var _Symbol = require("core-js-pure/features/symbol/index.js");
var _Symbol$asyncIterator = require("core-js-pure/features/symbol/async-iterator.js");
var OverloadYield = require("./OverloadYield.js");
var regeneratorDefine = require("./regeneratorDefine.js");
function AsyncIterator(t, e) {
	function n(r, o, i, f) {
		try {
			var c = t[r](o),
				u = c.value;
			return u instanceof OverloadYield
				? e.resolve(u.v).then(
						(t) => {
							n("next", t, i, f);
						},
						(t) => {
							n("throw", t, i, f);
						},
					)
				: e.resolve(u).then(
						(t) => {
							(c.value = t), i(c);
						},
						(t) => n("throw", t, i, f),
					);
		} catch (t) {
			f(t);
		}
	}
	var r;
	this.next ||
		(regeneratorDefine(AsyncIterator.prototype),
		regeneratorDefine(
			AsyncIterator.prototype,
			("function" == typeof _Symbol && _Symbol$asyncIterator) ||
				"@asyncIterator",
			function () {
				return this;
			},
		)),
		regeneratorDefine(
			this,
			"_invoke",
			(t, o, i) => {
				function f() {
					return new e((e, r) => {
						n(t, i, e, r);
					});
				}
				return (r = r ? r.then(f, f) : f());
			},
			!0,
		);
}
(module.exports = AsyncIterator),
	(module.exports.__esModule = true),
	(module.exports["default"] = module.exports);
