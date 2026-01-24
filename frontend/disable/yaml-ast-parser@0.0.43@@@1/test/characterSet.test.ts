import { assert } from "chai";
import * as YAML from "../src/";
import * as util from "./testUtil";

suite("YAML Syntax", () => {
	test("Allow astral characters", () => {
		const key = "𝑘𝑒𝑦";
		const value = "𝑣𝑎𝑙𝑢𝑒";
		const document = YAML.safeLoad(`${key}: ${value}`);

		assert.deepEqual(document.mappings[0].key.value, key);
		assert.deepEqual(document.mappings[0].value.value, value);
	});

	test("Forbid non-printable characters", () => {
		testErrors("\x01", [
			{
				line: 1,
				column: 0,
				message: "the stream contains non-printable characters",
				isWarning: false,
			},
		]);

		testErrors("\x7f", [
			{
				line: 1,
				column: 0,
				message: "the stream contains non-printable characters",
				isWarning: false,
			},
		]);

		testErrors("\x9f", [
			{
				line: 1,
				column: 0,
				message: "the stream contains non-printable characters",
				isWarning: false,
			},
		]);
	});

	test("Forbid lone surrogates", () => {
		testErrors("\udc00\ud800", [
			{
				line: 1,
				column: 0,
				message: "the stream contains non-printable characters",
				isWarning: false,
			},
		]);
	});

	test("Allow non-printable characters inside quoted scalars", () => {
		const key = '"\x7f\x9f\udc00\ud800"';
		const document = YAML.safeLoad(key);

		assert.deepEqual(document.value, "\x7f\x9f\udc00\ud800");
	});

	test("Forbid control sequences inside quoted scalars", () => {
		testErrors('"\x03"', [
			{
				line: 0,
				column: 2,
				message: "expected valid JSON character",
				isWarning: false,
			},
		]);
	});
});

function testErrors(input: string, expectedErrors: util.TestError[]) {
	util.testErrors(input, expectedErrors);
}
