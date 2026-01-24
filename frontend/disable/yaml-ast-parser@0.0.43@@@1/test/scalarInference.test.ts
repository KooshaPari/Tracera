import * as chai from "chai";

const assert = chai.assert;

import * as Yaml from "../src/index";
import {
	parseYamlBoolean,
	parseYamlFloat,
	parseYamlInteger,
	ScalarType,
	determineScalarType as sut,
} from "../src/scalarInference";

suite("determineScalarType", () => {
	function determineScalarType(scalar: Yaml.YAMLDocument) {
		return sut(<Yaml.YAMLScalar>scalar);
	}

	function safeLoad(input) {
		return Yaml.safeLoad(input, {});
	}

	const _test = test;

	// http://www.yaml.org/spec/1.2/spec.html#id2805071
	suite("Plain Tag Resolution", () => {
		function test(name, type, acceptable) {
			_test(name, () => {
				for (const word of acceptable) {
					assert.strictEqual(determineScalarType(safeLoad(word)), type, word);
				}
			});
		}

		test("boolean", ScalarType.bool, [
			"true",
			"True",
			"TRUE",
			"false",
			"False",
			"FALSE",
		]);

		test("null", ScalarType.null, ["null", "Null", "NULL", "~", ""]);
		_test("null as from an array", () => {
			const node = Yaml.newScalar("");
			node.plainScalar = true;
			assert.strictEqual(
				determineScalarType(node),
				ScalarType.null,
				"unquoted empty string",
			);
		});

		test("integer", ScalarType.int, ["0", "0o7", "0x3A", "-19"]);

		test("float", ScalarType.float, ["0.", "-0.0", ".5", "+12e03", "-2E+05"]);

		test("float-infinity", ScalarType.float, [".inf", "-.Inf", "+.INF"]);

		test("float-NaN", ScalarType.float, [".nan", ".NaN", ".NAN"]);

		test("string", ScalarType.string, [
			"'true'",
			"TrUe",
			"nULl",
			"''",
			"'0'",
			'"1"',
			'" .5"',
			".inF",
			".nAn",
		]);
	});

	suite("Flow style", () => {
		test("still recognizes types", () => {
			const node = <Yaml.YAMLSequence>safeLoad(`[ null,
  true,
  0,
  0.,
  .inf,
  .nan,
  "-123\n345"
]`);

			const expected = [
				ScalarType.null,
				ScalarType.bool,
				ScalarType.int,
				ScalarType.float,
				ScalarType.float,
				ScalarType.float,
				ScalarType.string,
			];

			assert.deepEqual(
				node.items.map((d) => determineScalarType(d)),
				expected,
			);
		});
	});

	suite("Block styles", () => {
		var variations = [">", "|", ">8", "|+1", ">-", ">+", "|-", "|+"];

		test("are always strings", () => {
			for (const variant of variations) {
				assert.deepEqual(
					determineScalarType(safeLoad(variant + "\n 123")),
					ScalarType.string,
				);
			}
		});
	});
});

suite("parseYamlInteger", () => {
	test("decimal", () => {
		assert.strictEqual(parseYamlInteger("0"), 0);
		assert.strictEqual(parseYamlInteger("-19"), -19);
		assert.strictEqual(parseYamlInteger("+1"), 1);
	});

	test("hexadecimal", () => {
		assert.strictEqual(parseYamlInteger("0x3A"), 58);
	});

	test("octal", () => {
		assert.strictEqual(parseYamlInteger("0o7"), 7);
	});

	test("otherwise", () => {
		let error;
		try {
			parseYamlInteger("'1'");
		} catch (e) {
			error = e;
		}

		assert(error, "should have thrown");
	});
});

suite("parseYamlBoolean", () => {
	test("true", () => {
		for (const value of ["true", "True", "TRUE"]) {
			assert.strictEqual(parseYamlBoolean(value), true, value);
		}
	});

	test("false", () => {
		for (const value of ["false", "False", "FALSE"]) {
			assert.strictEqual(parseYamlBoolean(value), false, value);
		}
	});

	test("otherwise", () => {
		let error;
		try {
			parseYamlBoolean("tRUE");
		} catch (e) {
			error = e;
		}

		assert(error, "should have thrown");
	});
});

suite("parseYamlFloat", () => {
	test("float", () => {
		const values = ["0.", "-0.0", ".5", "+12e03", "-2E+05"];
		const expected = [0, -0, 0.5, 12000, -200000];
		for (var index = 0; index < values.length; index++) {
			assert.strictEqual(parseYamlFloat(values[index]), expected[index]);
		}
	});

	test("NaN", () => {
		for (const value of [".nan", ".NaN", ".NAN"]) {
			assert(isNaN(parseYamlFloat(value)), `isNaN(${value})`);
		}
	});

	test("infinity", () => {
		assert.strictEqual(parseYamlFloat(".inf"), Infinity);
		assert.strictEqual(parseYamlFloat("-.Inf"), -Infinity);
		assert.strictEqual(parseYamlFloat(".INF"), Infinity);
	});

	test("otherwise", () => {
		let error;
		try {
			parseYamlFloat("text");
		} catch (e) {
			error = e;
		}

		assert(error, "should have thrown");
	});
});
