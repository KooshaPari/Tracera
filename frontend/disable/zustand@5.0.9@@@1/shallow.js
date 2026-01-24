"use strict";

var shallow = require("zustand/vanilla/shallow");
var shallow$1 = require("zustand/react/shallow");

Object.defineProperty(exports, "shallow", {
	enumerable: true,
	get: () => shallow.shallow,
});
Object.defineProperty(exports, "useShallow", {
	enumerable: true,
	get: () => shallow$1.useShallow,
});
