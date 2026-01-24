/*!
 * find-pkg <https://github.com/jonschlinkert/find-pkg>
 *
 * Copyright (c) 2015, Jon Schlinkert.
 * Licensed under the MIT License.
 */

/**
 * Module dependencies
 */

var findFile = require("find-file-up");

/**
 * Find package.json, starting with the given directory.
 * Based on https://github.com/jonschlinkert/look-up
 */

module.exports = (dir, limit, cb) => findFile("package.json", dir, limit, cb);

/**
 * Sync
 */

module.exports.sync = (dir, limit) => findFile.sync("package.json", dir, limit);
