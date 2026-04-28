#!/usr/bin/env bun

import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';

async function findPackageJsons(dir, depth = 0) {
  if (depth > 3) {
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
        files.push(...(await findPackageJsons(fullPath, depth + 1)));
      } else if (entry.name === 'package.json') {
        files.push(fullPath);
      }
    }
  } catch {
    // Skip
  }

  return files;
}

async function main() {
  const packageJsons = await findPackageJsons(process.cwd());

  // Large binary packages to check
  const largeBinaries = [
    'electron',
    'electron-builder',
    'next',
    '@next/swc-darwin-arm64',
    'monaco-editor',
    '@monaco-editor/react',
    'lighthouse',
    '@paulirish/lighthouse',
    'app-builder-bin',
    'electron-winstaller',
  ];

  const usageMap = new Map();

  for (const pkgPath of packageJsons) {
    try {
      const content = await readFile(pkgPath, 'utf8');
      const pkg = JSON.parse(content);
      const relativePath = pkgPath.replace(process.cwd(), '.');

      const allDeps = {
        ...pkg.dependencies,
        ...pkg.devDependencies,
      };

      for (const binary of largeBinaries) {
        if (allDeps[binary]) {
          if (!usageMap.has(binary)) {
            usageMap.set(binary, []);
          }
          usageMap.get(binary).push({
            path: relativePath,
            type: pkg.dependencies?.[binary] ? 'dependency' : 'devDependency',
            version: allDeps[binary],
          });
        }
      }
    } catch {
      // Skip
    }
  }

  for (const [pkg, locations] of usageMap.entries()) {
    locations.forEach(({ path, version, type }) => {});
  }

  if (usageMap.size === 0) {
  }
}

main();
