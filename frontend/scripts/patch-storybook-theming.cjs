#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..', 'node_modules', '@storybook', 'theming');
const nestedStorybook = path.join(root, 'node_modules', 'storybook');
const files = ['shim.js', 'shim.mjs', 'create.js', 'create.mjs', 'create.d.ts', 'shim.d.ts'];
const replacements = [
  ['storybook/internal/theming/create', 'storybook/theming/create'],
  ['storybook/internal/theming', 'storybook/theming'],
];

let changed = false;
for (const file of files) {
  const filePath = path.join(root, file);
  if (!fs.existsSync(filePath)) continue;
  let content = fs.readFileSync(filePath, 'utf8');
  let next = content;
  for (const [from, to] of replacements) {
    next = next.split(from).join(to);
  }
  if (next !== content) {
    fs.writeFileSync(filePath, next);
    changed = true;
  }
}

if (changed) {
  console.log('Patched @storybook/theming shims to use storybook/theming exports');
} else {
  console.log('storybook/theming shims already patched');
}

if (fs.existsSync(nestedStorybook)) {
  fs.rmSync(nestedStorybook, { recursive: true, force: true });
  console.log('Removed nested storybook from @storybook/theming');
}
