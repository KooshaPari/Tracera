const { describe, it } = require("mocha");
const assert = require("assert");
const path = require("path");
const requireInject = require("require-inject");
const { findAccessibleSync } = requireInject.withEmptyCache("../lib/util", {
	"graceful-fs": {
		closeSync: () => undefined,
		openSync: (path) => {
			if (readableFiles.some((f) => f === path)) {
				return 0;
			} else {
				const error = new Error("ENOENT - not found");
				throw error;
			}
		},
	},
});

const dir = path.sep + "testdir";
const readableFile = "readable_file";
const anotherReadableFile = "another_readable_file";
const readableFileInDir = "somedir" + path.sep + readableFile;
const readableFiles = [
	path.resolve(dir, readableFile),
	path.resolve(dir, anotherReadableFile),
	path.resolve(dir, readableFileInDir),
];

describe("find-accessible-sync", () => {
	it("find accessible - empty array", () => {
		const candidates = [];
		const found = findAccessibleSync("test", dir, candidates);
		assert.strictEqual(found, undefined);
	});

	it("find accessible - single item array, readable", () => {
		const candidates = [readableFile];
		const found = findAccessibleSync("test", dir, candidates);
		assert.strictEqual(found, path.resolve(dir, readableFile));
	});

	it("find accessible - single item array, readable in subdir", () => {
		const candidates = [readableFileInDir];
		const found = findAccessibleSync("test", dir, candidates);
		assert.strictEqual(found, path.resolve(dir, readableFileInDir));
	});

	it("find accessible - single item array, unreadable", () => {
		const candidates = ["unreadable_file"];
		const found = findAccessibleSync("test", dir, candidates);
		assert.strictEqual(found, undefined);
	});

	it("find accessible - multi item array, no matches", () => {
		const candidates = ["non_existent_file", "unreadable_file"];
		const found = findAccessibleSync("test", dir, candidates);
		assert.strictEqual(found, undefined);
	});

	it("find accessible - multi item array, single match", () => {
		const candidates = ["non_existent_file", readableFile];
		const found = findAccessibleSync("test", dir, candidates);
		assert.strictEqual(found, path.resolve(dir, readableFile));
	});

	it("find accessible - multi item array, return first match", () => {
		const candidates = ["non_existent_file", anotherReadableFile, readableFile];
		const found = findAccessibleSync("test", dir, candidates);
		assert.strictEqual(found, path.resolve(dir, anotherReadableFile));
	});
});
