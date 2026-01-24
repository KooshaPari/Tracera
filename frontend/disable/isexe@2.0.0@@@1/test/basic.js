var t = require("tap");
var fs = require("fs");
var path = require("path");
var fixture = path.resolve(__dirname, "fixtures");
var meow = fixture + "/meow.cat";
var mine = fixture + "/mine.cat";
var ours = fixture + "/ours.cat";
var fail = fixture + "/fail.false";
var noent = fixture + "/enoent.exe";
var mkdirp = require("mkdirp");
var rimraf = require("rimraf");

var isWindows = process.platform === "win32";
var hasAccess = typeof fs.access === "function";
var winSkip = isWindows && "windows";
var accessSkip = !hasAccess && "no fs.access function";
var hasPromise = typeof Promise === "function";
var promiseSkip = !hasPromise && "no global Promise";

function reset() {
	delete require.cache[require.resolve("../")];
	return require("../");
}

t.test("setup fixtures", (t) => {
	rimraf.sync(fixture);
	mkdirp.sync(fixture);
	fs.writeFileSync(meow, "#!/usr/bin/env cat\nmeow\n");
	fs.chmodSync(meow, 0o0755);
	fs.writeFileSync(fail, "#!/usr/bin/env false\n");
	fs.chmodSync(fail, 0o0644);
	fs.writeFileSync(mine, "#!/usr/bin/env cat\nmine\n");
	fs.chmodSync(mine, 0o0744);
	fs.writeFileSync(ours, "#!/usr/bin/env cat\nours\n");
	fs.chmodSync(ours, 0o0754);
	t.end();
});

t.test("promise", { skip: promiseSkip }, (t) => {
	var isexe = reset();
	t.test("meow async", (t) => {
		isexe(meow).then((is) => {
			t.ok(is);
			t.end();
		});
	});
	t.test("fail async", (t) => {
		isexe(fail).then((is) => {
			t.notOk(is);
			t.end();
		});
	});
	t.test("noent async", (t) => {
		isexe(noent).catch((er) => {
			t.ok(er);
			t.end();
		});
	});
	t.test("noent ignore async", (t) => {
		isexe(noent, { ignoreErrors: true }).then((is) => {
			t.notOk(is);
			t.end();
		});
	});
	t.end();
});

t.test("no promise", (t) => {
	global.Promise = null;
	var isexe = reset();
	t.throws("try to meow a promise", () => {
		isexe(meow);
	});
	t.end();
});

t.test("access", { skip: accessSkip || winSkip }, (t) => {
	runTest(t);
});

t.test("mode", { skip: winSkip }, (t) => {
	delete fs.access;
	delete fs.accessSync;
	var isexe = reset();
	t.ok(isexe.sync(ours, { uid: 0, gid: 0 }));
	t.ok(isexe.sync(mine, { uid: 0, gid: 0 }));
	runTest(t);
});

t.test("windows", (t) => {
	global.TESTING_WINDOWS = true;
	var pathExt = ".EXE;.CAT;.CMD;.COM";
	t.test("pathExt option", (t) => {
		runTest(t, { pathExt: ".EXE;.CAT;.CMD;.COM" });
	});
	t.test("pathExt env", (t) => {
		process.env.PATHEXT = pathExt;
		runTest(t);
	});
	t.test("no pathExt", (t) => {
		// with a pathExt of '', any filename is fine.
		// so the "fail" one would still pass.
		runTest(t, { pathExt: "", skipFail: true });
	});
	t.test("pathext with empty entry", (t) => {
		// with a pathExt of '', any filename is fine.
		// so the "fail" one would still pass.
		runTest(t, { pathExt: ";" + pathExt, skipFail: true });
	});
	t.end();
});

t.test("cleanup", (t) => {
	rimraf.sync(fixture);
	t.end();
});

function runTest(t, options) {
	var isexe = reset();

	var optionsIgnore = Object.create(options || {});
	optionsIgnore.ignoreErrors = true;

	if (!options || !options.skipFail) {
		t.notOk(isexe.sync(fail, options));
	}
	t.notOk(isexe.sync(noent, optionsIgnore));
	if (!options) {
		t.ok(isexe.sync(meow));
	} else {
		t.ok(isexe.sync(meow, options));
	}

	t.ok(isexe.sync(mine, options));
	t.ok(isexe.sync(ours, options));
	t.throws(() => {
		isexe.sync(noent, options);
	});

	t.test("meow async", (t) => {
		if (!options) {
			isexe(meow, (er, is) => {
				if (er) {
					throw er;
				}
				t.ok(is);
				t.end();
			});
		} else {
			isexe(meow, options, (er, is) => {
				if (er) {
					throw er;
				}
				t.ok(is);
				t.end();
			});
		}
	});

	t.test("mine async", (t) => {
		isexe(mine, options, (er, is) => {
			if (er) {
				throw er;
			}
			t.ok(is);
			t.end();
		});
	});

	t.test("ours async", (t) => {
		isexe(ours, options, (er, is) => {
			if (er) {
				throw er;
			}
			t.ok(is);
			t.end();
		});
	});

	if (!options || !options.skipFail) {
		t.test("fail async", (t) => {
			isexe(fail, options, (er, is) => {
				if (er) {
					throw er;
				}
				t.notOk(is);
				t.end();
			});
		});
	}

	t.test("noent async", (t) => {
		isexe(noent, options, (er, is) => {
			t.ok(er);
			t.notOk(is);
			t.end();
		});
	});

	t.test("noent ignore async", (t) => {
		isexe(noent, optionsIgnore, (er, is) => {
			if (er) {
				throw er;
			}
			t.notOk(is);
			t.end();
		});
	});

	t.test("directory is not executable", (t) => {
		isexe(__dirname, options, (er, is) => {
			if (er) {
				throw er;
			}
			t.notOk(is);
			t.end();
		});
	});

	t.end();
}
