#!/usr/bin/env node
/**
 * Patch doctrine to fix "TypeError: Middle is not a constructor" bug.
 * The issue is that doctrine/lib/utility.js uses an arrow function as a constructor
 * which doesn't work in modern Node.js ESM context.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const targetPath = path.join(__dirname, '..', 'node_modules', 'doctrine', 'lib', 'utility.js');

const MARKER = 'function Middle';
const ORIGINAL = `var Middle = () => {};`;
const PATCHED = `function Middle() {}`;

function patch(filePath) {
  if (!fs.existsSync(filePath)) {
    return;
  }
  let content = fs.readFileSync(filePath, 'utf8');
  if (content.includes(MARKER)) {
    return;
  }
  content = content.replace(ORIGINAL, PATCHED);
  fs.writeFileSync(filePath, content);
  console.log('Patched doctrine/lib/utility.js: fixed Middle constructor issue');
}

patch(targetPath);
