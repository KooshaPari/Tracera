#!/usr/bin/env bun

import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";

async function findPackageJsons(dir, depth = 0, maxDepth = 3) {
	if (depth > maxDepth) return [];

	const files = [];
	try {
		const entries = await readdir(dir, { withFileTypes: true });

		for (const entry of entries) {
			if (entry.name === "node_modules" || entry.name === ".git") continue;

			const fullPath = join(dir, entry.name);

			if (entry.isDirectory()) {
				files.push(...(await findPackageJsons(fullPath, depth + 1, maxDepth)));
			} else if (entry.name === "package.json") {
				files.push(fullPath);
			}
		}
	} catch {
		// Skip directories we can't read
	}

	return files;
}

async function analyzeDependencies() {
	const packageJsons = await findPackageJsons(process.cwd());

	const allDeps = new Map();
	const locations = new Map();

	for (const pkgPath of packageJsons) {
		try {
			const content = await readFile(pkgPath, "utf8");
			const pkg = JSON.parse(content);
			const relativePath = pkgPath.replace(process.cwd(), ".");

			const deps = {
				...pkg.dependencies,
				...pkg.devDependencies,
				...pkg.peerDependencies,
			};

			for (const [name, version] of Object.entries(deps)) {
				if (!allDeps.has(name)) {
					allDeps.set(name, new Set());
					locations.set(name, []);
				}
				allDeps.get(name).add(version);
				locations.get(name).push({ path: relativePath, version });
			}
		} catch {
			// Skip invalid JSON
		}
	}

	// Find duplicates
	const duplicates = [];
	const reactDeps = [];
	const typescriptDeps = [];

	for (const [name, versions] of allDeps.entries()) {
		if (versions.size > 1) {
			duplicates.push({
				name,
				versions: [...versions],
				locations: locations.get(name),
			});
		}

		if (name.includes("react") || name.includes("@types/react")) {
			reactDeps.push({
				name,
				versions: [...versions],
				locations: locations.get(name),
			});
		}

		if (name.includes("typescript") || name === "ts-node" || name === "tsx") {
			typescriptDeps.push({
				name,
				versions: [...versions],
				locations: locations.get(name),
			});
		}
	}

	console.log("=== DEPENDENCY ANALYSIS ===\n");
	console.log(`Total unique packages: ${allDeps.size}`);
	console.log(`Packages with version conflicts: ${duplicates.length}\n`);

	console.log("=== TOP 20 DUPLICATE DEPENDENCIES ===");
	duplicates
		.toSorted((a, b) => b.versions.length - a.versions.length)
		.slice(0, 20)
		.forEach(({ name, versions, locations }) => {
			console.log(`\n${name}:`);
			versions.forEach((v) => {
				const locs = locations.filter((l) => l.version === v);
				console.log(`  ${v} (${locs.length} locations)`);
			});
		});

	console.log("\n\n=== REACT DEPENDENCIES ===");
	reactDeps.forEach(({ name, versions, locations }) => {
		console.log(`\n${name}:`);
		versions.forEach((v) => {
			const locs = locations.filter((l) => l.version === v);
			console.log(`  ${v}: ${locs.map((l) => l.path).join(", ")}`);
		});
	});

	console.log("\n\n=== TYPESCRIPT DEPENDENCIES ===");
	typescriptDeps.forEach(({ name, versions, locations }) => {
		console.log(`\n${name}:`);
		versions.forEach((v) => {
			const locs = locations.filter((l) => l.version === v);
			console.log(`  ${v}: ${locs.map((l) => l.path).join(", ")}`);
		});
	});

	// Generate report file
	const report = {
		summary: {
			totalPackages: allDeps.size,
			duplicates: duplicates.length,
			timestamp: new Date().toISOString(),
		},
		duplicates,
		reactDeps,
		typescriptDeps,
	};

	await Bun.write("dependency-analysis.json", JSON.stringify(report, undefined, 2));
	console.log("\n\nDetailed report saved to: dependency-analysis.json");
}

try {
	await analyzeDependencies();
} catch (err) {
	console.error(err);
	process.exitCode = 1;
}
