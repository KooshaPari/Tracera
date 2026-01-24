"use strict";
var defineProperty = require("../internals/object-define-property").f;

module.exports = (Target, Source, key) => {
	key in Target ||
		defineProperty(Target, key, {
			configurable: true,
			get: () => Source[key],
			set: (it) => {
				Source[key] = it;
			},
		});
};
