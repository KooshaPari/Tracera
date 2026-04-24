#!/usr/bin/env bun

import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';

async function findPackageJsons(dir, depth = 0, maxDepth = 3) {
  if (depth > maxDepth) {
    return [];
  }

  const files = [];
  try {
    const entries = await readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.name === 'node_modules' || entry.name === '.git') {
        continue;
      }

      const fullPath = join(dir, entry.name);

      if (entry.isDirectory()) {
        files.push(...(await findPackageJsons(fullPath, depth + 1, maxDepth)));
      } else if (entry.name === 'package.json') {
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
      const content = await readFile(pkgPath, 'utf8');
      const pkg = JSON.parse(content);
      const relativePath = pkgPath.replace(process.cwd(), '.');

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
        locations: locations.get(name),
        name,
        versions: [...versions],
      });
    }

    if (name.includes('react') || name.includes('@types/react')) {
      reactDeps.push({
        locations: locations.get(name),
        name,
        versions: [...versions],
      });
    }

    if (name.includes('typescript') || name === 'ts-node' || name === 'tsx') {
      typescriptDeps.push({
        locations: locations.get(name),
        name,
        versions: [...versions],
      });
    }
  }

  duplicates
    .toSorted((a, b) => b.versions.length - a.versions.length)
    .slice(0, 20)
    .forEach(({ name, versions, locations }) => {
      versions.forEach((v) => {
        const locs = locations.filter((l) => l.version === v);
      });
    });

  reactDeps.forEach(({ name, versions, locations }) => {
    versions.forEach((v) => {
      const locs = locations.filter((l) => l.version === v);
    });
  });

  typescriptDeps.forEach(({ name, versions, locations }) => {
    versions.forEach((v) => {
      const locs = locations.filter((l) => l.version === v);
    });
  });

  // Generate report file
  const report = {
    duplicates,
    reactDeps,
    summary: {
      duplicates: duplicates.length,
      timestamp: new Date().toISOString(),
      totalPackages: allDeps.size,
    },
    typescriptDeps,
  };

  await Bun.write('dependency-analysis.json', JSON.stringify(report, undefined, 2));
}

try {
  await analyzeDependencies();
} catch (error) {
  console.error(error);
  process.exitCode = 1;
}
