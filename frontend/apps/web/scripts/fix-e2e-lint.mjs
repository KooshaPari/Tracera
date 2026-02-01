#!/usr/bin/env node
/**
 * One-time script to apply e2e lint fixes when biome check --write --unsafe
 * doesn't run (e.g. different working copy). Run from frontend/apps/web:
 *   node scripts/fix-e2e-lint.mjs
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");

const fixes = [
	{
		file: "e2e/table-accessibility.spec.ts",
		from: '.withRules(["landmark-one-main", "region"]\')',
		to: '.withRules(["landmark-one-main", "region"])',
	},
	{
		file: "e2e/performance.spec.ts",
		from: 'if (cacheControl && cacheControl.includes("max-age")) {',
		to: 'if (cacheControl?.includes("max-age")) {',
	},
	{
		file: "e2e/auth-flow.spec.ts",
		from: 'import type { BrowserContext, Page } from "@playwright/test";\nimport { expect, test } from "./global-setup";',
		to: 'import { expect, test } from "./global-setup";',
	},
	{
		file: "e2e/component-library.spec.ts",
		from: 'import { expect, test } from "./global-setup";',
		to: 'import { test } from "./global-setup";',
	},
	{
		file: "e2e/equivalence.spec.ts",
		from: 'import { expect, test } from "./global-setup";',
		to: 'import { test } from "./global-setup";',
	},
	{
		file: "e2e/journey-overlay.spec.ts",
		from: 'import { expect, test } from "./global-setup";',
		to: 'import { test } from "./global-setup";',
	},
	{
		file: "e2e/mobile-optimization.spec.ts",
		from: 'import { expect, Page, test } from "@playwright/test";',
		to: 'import { expect, test } from "@playwright/test";',
	},
	{
		file: "e2e/screenshot-storage.spec.ts",
		from: 'import { expect, Page, test } from "@playwright/test";',
		to: 'import { expect, test } from "@playwright/test";',
	},
];

let applied = 0;
for (const { file, from, to } of fixes) {
	const filePath = path.join(root, file);
	try {
		let content = readFileSync(filePath, "utf8");
		if (content.includes(from)) {
			content = content.replace(from, to);
			writeFileSync(filePath, content);
			applied++;
			console.log("Fixed:", file);
		}
	} catch (e) {
		if (e.code !== "ENOENT") console.error(file, e.message);
	}
}
console.log(
	applied
		? `Applied ${applied} fix(es).`
		: "No matching content to fix (files may already be fixed).",
);
