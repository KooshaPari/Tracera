#!/usr/bin/env node
// Patch @tanstack/router-generator to work with Zod 4
// Issue: router-generator uses z.function().returns() which doesn't exist in Zod 4

import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const configPath = join(
	process.cwd(),
	"node_modules/@tanstack/router-generator/dist/esm/config.js",
);

try {
	const content = readFileSync(configPath, "utf8");

	// Replace z.function().returns() with Zod 4 equivalent
	// Old: z.function().returns(z.string())
	// New: z.function(z.tuple([]), z.string())

	const patched = content.replaceAll(
		/z\.function\(\)\.returns\((.*?)\)/g,
		"z.function(z.tuple([]), $1)",
	);

	if (content !== patched) {
		writeFileSync(configPath, patched, "utf8");
	} else {
	}
} catch (error) {
	process.exit(0); // Don't fail build
}
