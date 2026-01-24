var implementation = require("../implementation");
var test = require("tape");
var runTests = require("./tests");

test("implementation", (t) => {
	runTests(implementation, t);

	t.end();
});
