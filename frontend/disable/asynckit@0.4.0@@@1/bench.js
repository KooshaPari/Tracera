/* eslint no-console: "off" */

var asynckit = require("./"),
	async = require("async"),
	assert = require("assert"),
	expected = 0;

var Benchmark = require("benchmark");
var suite = new Benchmark.Suite();

var source = [];
for (var z = 1; z < 100; z++) {
	source.push(z);
	expected += z;
}

suite
	// add tests

	.add(
		"async.map",
		(deferred) => {
			var total = 0;

			async.map(
				source,
				(i, cb) => {
					setImmediate(() => {
						total += i;
						cb(null, total);
					});
				},
				(err, result) => {
					assert.ifError(err);
					assert.equal(result[result.length - 1], expected);
					deferred.resolve();
				},
			);
		},
		{ defer: true },
	)

	.add(
		"asynckit.parallel",
		(deferred) => {
			var total = 0;

			asynckit.parallel(
				source,
				(i, cb) => {
					setImmediate(() => {
						total += i;
						cb(null, total);
					});
				},
				(err, result) => {
					assert.ifError(err);
					assert.equal(result[result.length - 1], expected);
					deferred.resolve();
				},
			);
		},
		{ defer: true },
	)

	// add listeners
	.on("cycle", (ev) => {
		console.log(String(ev.target));
	})
	.on("complete", function () {
		console.log("Fastest is " + this.filter("fastest").map("name"));
	})
	// run async
	.run({ async: true });
