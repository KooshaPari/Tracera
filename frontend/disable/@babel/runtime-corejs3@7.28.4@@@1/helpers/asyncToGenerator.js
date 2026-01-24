var _Promise = require("core-js-pure/features/promise/index.js");
function asyncGeneratorStep(n, t, e, r, o, a, c) {
	try {
		var i = n[a](c),
			u = i.value;
	} catch (n) {
		return void e(n);
	}
	i.done ? t(u) : _Promise.resolve(u).then(r, o);
}
function _asyncToGenerator(n) {
	return function () {
		var e = arguments;
		return new _Promise((r, o) => {
			var a = n.apply(this, e);
			function _next(n) {
				asyncGeneratorStep(a, r, o, _next, _throw, "next", n);
			}
			function _throw(n) {
				asyncGeneratorStep(a, r, o, _next, _throw, "throw", n);
			}
			_next(void 0);
		});
	};
}
(module.exports = _asyncToGenerator),
	(module.exports.__esModule = true),
	(module.exports["default"] = module.exports);
