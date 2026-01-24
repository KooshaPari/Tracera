"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateOptions = generateOptions;
function generateOptions(options, defaults) {
	if (typeof options === "function") {
		defaults.callback = options;
	} else if (options) {
		for (var name in options) {
			/* istanbul ignore else */
			if (Object.hasOwn(options, name)) {
				defaults[name] = options[name];
			}
		}
	}
	return defaults;
}
