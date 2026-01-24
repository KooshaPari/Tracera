"use strict";

exports.__esModule = true;
var _nodeFs = require("node:fs");
Object.keys(_nodeFs).forEach((key) => {
	if (key === "default" || key === "__esModule") return;
	if (key in exports && exports[key] === _nodeFs[key]) return;
	exports[key] = _nodeFs[key];
});
