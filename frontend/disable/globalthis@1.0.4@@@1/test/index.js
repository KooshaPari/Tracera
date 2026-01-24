var systemGlobal = require("../");
var test = require("tape");
var runTests = require("./tests");

test("as a function", (t) => {
	runTests(systemGlobal(), t);

	t.end();
});
