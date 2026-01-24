var defineProperty = require("./defineProperty.js");
function _objectSpread(e) {
	for (var r = 1; r < arguments.length; r++) {
		var t = null != arguments[r] ? Object(arguments[r]) : {},
			o = Object.keys(t);
		"function" == typeof Object.getOwnPropertySymbols &&
			o.push.apply(
				o,
				Object.getOwnPropertySymbols(t).filter(
					(e) => Object.getOwnPropertyDescriptor(t, e).enumerable,
				),
			),
			o.forEach((r) => {
				defineProperty(e, r, t[r]);
			});
	}
	return e;
}
(module.exports = _objectSpread),
	(module.exports.__esModule = true),
	(module.exports["default"] = module.exports);
