"use strict";

Object.defineProperty(exports, "__esModule", {
	value: true,
});
exports.default = _isNativeReflectConstruct;
function _isNativeReflectConstruct() {
	try {
		var result = !Boolean.prototype.valueOf.call(
			Reflect.construct(Boolean, [], () => {}),
		);
	} catch (_) {}
	return (exports.default = _isNativeReflectConstruct = () => !!result)();
}

//# sourceMappingURL=isNativeReflectConstruct.js.map
