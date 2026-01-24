#!/usr/bin/env node

const importLocal = require("..");

if (importLocal(__filename)) {
	console.log("local");
}
