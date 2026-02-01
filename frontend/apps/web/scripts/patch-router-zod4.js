#!/usr/bin/env node
// Patch @tanstack/router-generator to work with Zod 4
// Issue: router-generator uses z.function().returns() which doesn't exist in Zod 4

import { readFileSync, writeFileSync } from "fs";
import { join } from "path";

const configPath = join(
	process.cwd(),
	"node_modules/@tanstack/router-generator/dist/esm/config.js",
);

try {
	const content = readFileSync(configPath, "utf8");

	// Replace z.function().returns() with Zod 4 equivalent
	// Old: z.function().returns(z.string())
	// New: z.function(z.tuple([]), z.string())

	const patched = content.replace(
		/z\.function\(\)\.returns\((.*?)\)/g,
		"z.function(z.tuple([]), $1)",
	);

	if (content !== patched) {
		writeFileSync(configPath, patched, "utf8");
		console.log(
			"✅ Patched @tanstack/router-generator for Zod 4 compatibility",
		);
	} else {
		console.log("ℹ️  No patching needed or already patched");
	}
} catch (error) {
	console.error("❌ Failed to patch router-generator:", error.message);
	process.exit(0); // Don't fail build
}
