#!/usr/bin/env node
// Patch @tanstack/router-generator to work with Zod 4
// Issue: router-generator uses z.function().returns() which doesn't exist in Zod 4

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const locateConfig = (startDir) => {
  let current = startDir;
  for (let i = 0; i < 6; i += 1) {
    const candidate = join(current, 'node_modules/@tanstack/router-generator/dist/esm/config.js');
    if (existsSync(candidate)) {
      return candidate;
    }
    const parent = dirname(current);
    if (parent === current) {
      break;
    }
    current = parent;
  }
  return null;
};

try {
  const scriptDir = dirname(fileURLToPath(import.meta.url));
  const configPath = locateConfig(process.cwd()) ?? locateConfig(scriptDir);
  if (!configPath) {
    process.exit(0);
  }

  const content = readFileSync(configPath, 'utf8');

  // Replace z.function().returns() with Zod 4 equivalent
  // Old: z.function().returns(z.string())
  // New: z.function(z.tuple([]), z.string())

  const patched = content.replaceAll(
    /z\.function\(\)\.returns\((.*?)\)/g,
    'z.function(z.tuple([]), $1)',
  );

  if (content !== patched) {
    writeFileSync(configPath, patched, 'utf8');
  } else {
  }
} catch {
  process.exit(0); // Don't fail build
}
