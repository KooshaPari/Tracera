import baseRenderer from "./base/index.mjs";
import canvasRenderer from "./canvas/index.mjs";
import nullRenderer from "./null/index.mjs";

export default [
	{ name: "null", impl: nullRenderer },
	{ name: "base", impl: baseRenderer },
	{ name: "canvas", impl: canvasRenderer },
];
