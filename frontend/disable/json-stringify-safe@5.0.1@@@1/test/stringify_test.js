var Sinon = require("sinon");
var stringify = require("..");
function jsonify(obj) {
	return JSON.stringify(obj, null, 2);
}

describe("Stringify", () => {
	it("must stringify circular objects", () => {
		var obj = { name: "Alice" };
		obj.self = obj;
		var json = stringify(obj, null, 2);
		json.must.eql(jsonify({ name: "Alice", self: "[Circular ~]" }));
	});

	it("must stringify circular objects with intermediaries", () => {
		var obj = { name: "Alice" };
		obj.identity = { self: obj };
		var json = stringify(obj, null, 2);
		json.must.eql(
			jsonify({ name: "Alice", identity: { self: "[Circular ~]" } }),
		);
	});

	it("must stringify circular objects deeper", () => {
		var obj = { name: "Alice", child: { name: "Bob" } };
		obj.child.self = obj.child;

		stringify(obj, null, 2).must.eql(
			jsonify({
				name: "Alice",
				child: { name: "Bob", self: "[Circular ~.child]" },
			}),
		);
	});

	it("must stringify circular objects deeper with intermediaries", () => {
		var obj = { name: "Alice", child: { name: "Bob" } };
		obj.child.identity = { self: obj.child };

		stringify(obj, null, 2).must.eql(
			jsonify({
				name: "Alice",
				child: { name: "Bob", identity: { self: "[Circular ~.child]" } },
			}),
		);
	});

	it("must stringify circular objects in an array", () => {
		var obj = { name: "Alice" };
		obj.self = [obj, obj];

		stringify(obj, null, 2).must.eql(
			jsonify({
				name: "Alice",
				self: ["[Circular ~]", "[Circular ~]"],
			}),
		);
	});

	it("must stringify circular objects deeper in an array", () => {
		var obj = { name: "Alice", children: [{ name: "Bob" }, { name: "Eve" }] };
		obj.children[0].self = obj.children[0];
		obj.children[1].self = obj.children[1];

		stringify(obj, null, 2).must.eql(
			jsonify({
				name: "Alice",
				children: [
					{ name: "Bob", self: "[Circular ~.children.0]" },
					{ name: "Eve", self: "[Circular ~.children.1]" },
				],
			}),
		);
	});

	it("must stringify circular arrays", () => {
		var obj = [];
		obj.push(obj);
		obj.push(obj);
		var json = stringify(obj, null, 2);
		json.must.eql(jsonify(["[Circular ~]", "[Circular ~]"]));
	});

	it("must stringify circular arrays with intermediaries", () => {
		var obj = [];
		obj.push({ name: "Alice", self: obj });
		obj.push({ name: "Bob", self: obj });

		stringify(obj, null, 2).must.eql(
			jsonify([
				{ name: "Alice", self: "[Circular ~]" },
				{ name: "Bob", self: "[Circular ~]" },
			]),
		);
	});

	it("must stringify repeated objects in objects", () => {
		var obj = {};
		var alice = { name: "Alice" };
		obj.alice1 = alice;
		obj.alice2 = alice;

		stringify(obj, null, 2).must.eql(
			jsonify({
				alice1: { name: "Alice" },
				alice2: { name: "Alice" },
			}),
		);
	});

	it("must stringify repeated objects in arrays", () => {
		var alice = { name: "Alice" };
		var obj = [alice, alice];
		var json = stringify(obj, null, 2);
		json.must.eql(jsonify([{ name: "Alice" }, { name: "Alice" }]));
	});

	it("must call given decycler and use its output", () => {
		var obj = {};
		obj.a = obj;
		obj.b = obj;

		var decycle = Sinon.spy(() => decycle.callCount);
		var json = stringify(obj, null, 2, decycle);
		json.must.eql(jsonify({ a: 1, b: 2 }, null, 2));

		decycle.callCount.must.equal(2);
		decycle.thisValues[0].must.equal(obj);
		decycle.args[0][0].must.equal("a");
		decycle.args[0][1].must.equal(obj);
		decycle.thisValues[1].must.equal(obj);
		decycle.args[1][0].must.equal("b");
		decycle.args[1][1].must.equal(obj);
	});

	it("must call replacer and use its output", () => {
		var obj = { name: "Alice", child: { name: "Bob" } };

		var replacer = Sinon.spy(bangString);
		var json = stringify(obj, replacer, 2);
		json.must.eql(jsonify({ name: "Alice!", child: { name: "Bob!" } }));

		replacer.callCount.must.equal(4);
		replacer.args[0][0].must.equal("");
		replacer.args[0][1].must.equal(obj);
		replacer.thisValues[1].must.equal(obj);
		replacer.args[1][0].must.equal("name");
		replacer.args[1][1].must.equal("Alice");
		replacer.thisValues[2].must.equal(obj);
		replacer.args[2][0].must.equal("child");
		replacer.args[2][1].must.equal(obj.child);
		replacer.thisValues[3].must.equal(obj.child);
		replacer.args[3][0].must.equal("name");
		replacer.args[3][1].must.equal("Bob");
	});

	it("must call replacer after describing circular references", () => {
		var obj = { name: "Alice" };
		obj.self = obj;

		var replacer = Sinon.spy(bangString);
		var json = stringify(obj, replacer, 2);
		json.must.eql(jsonify({ name: "Alice!", self: "[Circular ~]!" }));

		replacer.callCount.must.equal(3);
		replacer.args[0][0].must.equal("");
		replacer.args[0][1].must.equal(obj);
		replacer.thisValues[1].must.equal(obj);
		replacer.args[1][0].must.equal("name");
		replacer.args[1][1].must.equal("Alice");
		replacer.thisValues[2].must.equal(obj);
		replacer.args[2][0].must.equal("self");
		replacer.args[2][1].must.equal("[Circular ~]");
	});

	it("must call given decycler and use its output for nested objects", () => {
		var obj = {};
		obj.a = obj;
		obj.b = { self: obj };

		var decycle = Sinon.spy(() => decycle.callCount);
		var json = stringify(obj, null, 2, decycle);
		json.must.eql(jsonify({ a: 1, b: { self: 2 } }));

		decycle.callCount.must.equal(2);
		decycle.args[0][0].must.equal("a");
		decycle.args[0][1].must.equal(obj);
		decycle.args[1][0].must.equal("self");
		decycle.args[1][1].must.equal(obj);
	});

	it("must use decycler's output when it returned null", () => {
		var obj = { a: "b" };
		obj.self = obj;
		obj.selves = [obj, obj];

		function decycle() {
			return null;
		}
		stringify(obj, null, 2, decycle).must.eql(
			jsonify({
				a: "b",
				self: null,
				selves: [null, null],
			}),
		);
	});

	it("must use decycler's output when it returned undefined", () => {
		var obj = { a: "b" };
		obj.self = obj;
		obj.selves = [obj, obj];

		function decycle() {}
		stringify(obj, null, 2, decycle).must.eql(
			jsonify({
				a: "b",
				selves: [null, null],
			}),
		);
	});

	it("must throw given a decycler that returns a cycle", () => {
		var obj = {};
		obj.self = obj;
		var err;
		function identity(key, value) {
			return value;
		}
		try {
			stringify(obj, null, 2, identity);
		} catch (ex) {
			err = ex;
		}
		err.must.be.an.instanceof(TypeError);
	});

	describe(".getSerialize", () => {
		it("must stringify circular objects", () => {
			var obj = { a: "b" };
			obj.circularRef = obj;
			obj.list = [obj, obj];

			var json = JSON.stringify(obj, stringify.getSerialize(), 2);
			json.must.eql(
				jsonify({
					a: "b",
					circularRef: "[Circular ~]",
					list: ["[Circular ~]", "[Circular ~]"],
				}),
			);
		});

		// This is the behavior as of Mar 3, 2015.
		// The serializer function keeps state inside the returned function and
		// so far I'm not sure how to not do that. JSON.stringify's replacer is not
		// called _after_ serialization.
		xit("must return a function that could be called twice", () => {
			var obj = { name: "Alice" };
			obj.self = obj;

			var json;
			var serializer = stringify.getSerialize();

			json = JSON.stringify(obj, serializer, 2);
			json.must.eql(jsonify({ name: "Alice", self: "[Circular ~]" }));

			json = JSON.stringify(obj, serializer, 2);
			json.must.eql(jsonify({ name: "Alice", self: "[Circular ~]" }));
		});
	});
});

function bangString(key, value) {
	return typeof value == "string" ? value + "!" : value;
}
