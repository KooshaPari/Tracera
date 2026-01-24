/**
 * archiver-utils
 *
 * Copyright (c) 2015 Chris Talkington.
 * Licensed under the MIT license.
 * https://github.com/archiverjs/archiver-utils/blob/master/LICENSE
 */
var fs = require("graceful-fs");
var path = require("path");
var nutil = require("util");
var lazystream = require("lazystream");
var normalizePath = require("normalize-path");
var defaults = require("lodash.defaults");

var Stream = require("stream").Stream;
var PassThrough = require("readable-stream").PassThrough;

var utils = (module.exports = {});
utils.file = require("./file.js");

function assertPath(path) {
	if (typeof path !== "string") {
		throw new TypeError(
			"Path must be a string. Received " + nutils.inspect(path),
		);
	}
}

utils.collectStream = (source, callback) => {
	var collection = [];
	var size = 0;

	source.on("error", callback);

	source.on("data", (chunk) => {
		collection.push(chunk);
		size += chunk.length;
	});

	source.on("end", () => {
		var buf = new Buffer(size);
		var offset = 0;

		collection.forEach((data) => {
			data.copy(buf, offset);
			offset += data.length;
		});

		callback(null, buf);
	});
};

utils.dateify = (dateish) => {
	dateish = dateish || new Date();

	if (dateish instanceof Date) {
		dateish = dateish;
	} else if (typeof dateish === "string") {
		dateish = new Date(dateish);
	} else {
		dateish = new Date();
	}

	return dateish;
};

// this is slightly different from lodash version
utils.defaults = function (object, source, guard) {
	var args = arguments;
	args[0] = args[0] || {};

	return defaults(...args);
};

utils.isStream = (source) => source instanceof Stream;

utils.lazyReadStream = (filepath) =>
	new lazystream.Readable(() => fs.createReadStream(filepath));

utils.normalizeInputSource = (source) => {
	if (source === null) {
		return new Buffer(0);
	} else if (typeof source === "string") {
		return new Buffer(source);
	} else if (utils.isStream(source) && !source._readableState) {
		var normalized = new PassThrough();
		source.pipe(normalized);

		return normalized;
	}

	return source;
};

utils.sanitizePath = (filepath) =>
	normalizePath(filepath, false)
		.replace(/^\w+:/, "")
		.replace(/^(\.\.\/|\/)+/, "");

utils.trailingSlashIt = (str) => (str.slice(-1) !== "/" ? str + "/" : str);

utils.unixifyPath = (filepath) =>
	normalizePath(filepath, false).replace(/^\w+:/, "");

utils.walkdir = (dirpath, base, callback) => {
	var results = [];

	if (typeof base === "function") {
		callback = base;
		base = dirpath;
	}

	fs.readdir(dirpath, (err, list) => {
		var i = 0;
		var file;
		var filepath;

		if (err) {
			return callback(err);
		}

		(function next() {
			file = list[i++];

			if (!file) {
				return callback(null, results);
			}

			filepath = path.join(dirpath, file);

			fs.stat(filepath, (err, stats) => {
				results.push({
					path: filepath,
					relative: path.relative(base, filepath).replace(/\\/g, "/"),
					stats: stats,
				});

				if (stats && stats.isDirectory()) {
					utils.walkdir(filepath, base, (err, res) => {
						res.forEach((dirEntry) => {
							results.push(dirEntry);
						});
						next();
					});
				} else {
					next();
				}
			});
		})();
	});
};
