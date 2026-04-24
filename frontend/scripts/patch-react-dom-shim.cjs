#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const pkgPath = path.join(
  __dirname,
  '..',
  'node_modules',
  '@storybook',
  'react-dom-shim',
  'package.json',
);
if (!fs.existsSync(pkgPath)) {
  process.exit(0);
}

const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const exportsField = pkg.exports || {};

if (!exportsField['./dist/preset']) {
  exportsField['./dist/preset'] = './dist/preset.js';
  pkg.exports = exportsField;
  fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n');
  console.log('Patched @storybook/react-dom-shim exports to include ./dist/preset');
} else {
  console.log('react-dom-shim exports already include ./dist/preset');
}
