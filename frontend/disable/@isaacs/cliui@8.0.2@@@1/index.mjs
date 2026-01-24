// Bootstrap cliui with ESM dependencies:

import stringWidth from "string-width";
import stripAnsi from "strip-ansi";
import wrap from "wrap-ansi";
import { cliui } from "./build/lib/index.js";

export default function ui(opts) {
	return cliui(opts, {
		stringWidth,
		stripAnsi,
		wrap,
	});
}
