var assert = require("assert");
var delegate = require("..");

describe(".method(name)", () => {
	it("should delegate methods", () => {
		var obj = {};

		obj.request = {
			foo: function (bar) {
				assert(this == obj.request);
				return bar;
			},
		};

		delegate(obj, "request").method("foo");

		obj.foo("something").should.equal("something");
	});
});

describe(".getter(name)", () => {
	it("should delegate getters", () => {
		var obj = {};

		obj.request = {
			get type() {
				return "text/html";
			},
		};

		delegate(obj, "request").getter("type");

		obj.type.should.equal("text/html");
	});
});

describe(".setter(name)", () => {
	it("should delegate setters", () => {
		var obj = {};

		obj.request = {
			get type() {
				return this._type.toUpperCase();
			},

			set type(val) {
				this._type = val;
			},
		};

		delegate(obj, "request").setter("type");

		obj.type = "hey";
		obj.request.type.should.equal("HEY");
	});
});

describe(".access(name)", () => {
	it("should delegate getters and setters", () => {
		var obj = {};

		obj.request = {
			get type() {
				return this._type.toUpperCase();
			},

			set type(val) {
				this._type = val;
			},
		};

		delegate(obj, "request").access("type");

		obj.type = "hey";
		obj.type.should.equal("HEY");
	});
});

describe(".fluent(name)", () => {
	it("should delegate in a fluent fashion", () => {
		var obj = {
			settings: {
				env: "development",
			},
		};

		delegate(obj, "settings").fluent("env");

		obj.env().should.equal("development");
		obj.env("production").should.equal(obj);
		obj.settings.env.should.equal("production");
	});
});
