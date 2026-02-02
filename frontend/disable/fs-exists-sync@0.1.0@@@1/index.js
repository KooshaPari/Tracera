/*!
 * fs-exists-sync (https://github.com/jonschlinkert/fs-exists-sync)
 *
 * Copyright (c) 2016, Jon Schlinkert.
 * Licensed under the MIT License.
 */

var fs = require("fs");

module.exports = (filepath) => {
	try {
		(fs.accessSync || fs.statSync)(filepath);
		return true;
	} catch (_err) {}
	return false;
};
