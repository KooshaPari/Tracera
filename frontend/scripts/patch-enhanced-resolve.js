import { globSync } from 'glob';
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();

const explicitFiles = [
  path.join(root, 'node_modules', 'enhanced-resolve', 'lib', 'SyncAsyncFileSystemDecorator.js'),
  path.join(root, 'node_modules', 'enhanced-resolve', 'lib', 'CachedInputFileSystem.js'),
];

const docsDecoratorFiles = globSync(
  path.join(
    root,
    'apps',
    'docs',
    'node_modules',
    '.pnpm',
    'enhanced-resolve@*',
    'node_modules',
    'enhanced-resolve',
    'lib',
    'SyncAsyncFileSystemDecorator.js',
  ),
);

const docsCachedFiles = globSync(
  path.join(
    root,
    'apps',
    'docs',
    'node_modules',
    '.pnpm',
    'enhanced-resolve@*',
    'node_modules',
    'enhanced-resolve',
    'lib',
    'CachedInputFileSystem.js',
  ),
);

const decoratorFiles = [
  ...explicitFiles.filter((file) => file.endsWith('SyncAsyncFileSystemDecorator.js')),
  ...docsDecoratorFiles,
];
const cachedFiles = [
  ...explicitFiles.filter((file) => file.endsWith('CachedInputFileSystem.js')),
  ...docsCachedFiles,
];

let didPatch = false;

for (const file of decoratorFiles) {
  if (!fs.existsSync(file)) continue;
  const source = fs.readFileSync(file, 'utf8');
  const updated = source.replace(/\(err\)/g, '(_err)');
  if (updated !== source) {
    fs.writeFileSync(file, updated, 'utf8');
    didPatch = true;
  }
}

for (const file of cachedFiles) {
  if (!fs.existsSync(file)) continue;
  const source = fs.readFileSync(file, 'utf8');
  // ponytail: some published enhanced-resolve versions have a catch block whose
  // `catch (err) { ... }` header doesn't match the identifier used in the body
  // (upstream copy-paste bug), which throws "ReferenceError: _err/err is not
  // defined" at build time. Rather than assume a fixed before/after string pair
  // (which breaks the moment the upstream source shifts, as happened on the
  // 5.18.4 -> 5.24.1 bump), rewrite the catch header to bind whichever
  // identifier ("_err" or "err") the block body actually references.
  const updated = source.replace(
    /catch \((?:_err|err)\) (\{(?:[^{}]|\{[^{}]*\})*\})/g,
    (full, block) => {
      const usesUnderscoreErr = /\b_err\b/.test(block);
      const usesErr = /(?<!_)\berr\b/.test(block);
      if (usesUnderscoreErr && !usesErr) return full.replace('catch (err)', 'catch (_err)').replace('catch (_err)', 'catch (_err)');
      if (usesErr && !usesUnderscoreErr) return full.replace('catch (_err)', 'catch (err)');
      return full;
    },
  );

  if (updated !== source) {
    fs.writeFileSync(file, updated, 'utf8');
    didPatch = true;
  }
}

if (didPatch) {
  console.log('patch-enhanced-resolve: patched successfully');
} else {
  console.log('patch-enhanced-resolve: already patched or unexpected format');
}
