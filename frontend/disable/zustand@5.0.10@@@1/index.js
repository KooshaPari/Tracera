"use strict";

var vanilla = require("zustand/vanilla");
var react = require("zustand/react");

Object.keys(vanilla).forEach((k) => {
	if (k !== "default" && !Object.hasOwn(exports, k))
		Object.defineProperty(exports, k, {
			enumerable: true,
			get: () => vanilla[k],
		});
});
Object.keys(react).forEach((k) => {
	if (k !== "default" && !Object.hasOwn(exports, k))
		Object.defineProperty(exports, k, {
			enumerable: true,
			get: () => react[k],
		});
});
