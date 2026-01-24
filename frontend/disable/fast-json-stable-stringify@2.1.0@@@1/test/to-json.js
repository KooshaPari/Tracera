var test = require("tape");
var stringify = require("../");

test("toJSON function", (t) => {
	t.plan(1);
	var obj = {
		one: 1,
		two: 2,
		toJSON: () => ({ one: 1 }),
	};
	t.equal(stringify(obj), '{"one":1}');
});

test("toJSON returns string", (t) => {
	t.plan(1);
	var obj = {
		one: 1,
		two: 2,
		toJSON: () => "one",
	};
	t.equal(stringify(obj), '"one"');
});

test("toJSON returns array", (t) => {
	t.plan(1);
	var obj = {
		one: 1,
		two: 2,
		toJSON: () => ["one"],
	};
	t.equal(stringify(obj), '["one"]');
});
