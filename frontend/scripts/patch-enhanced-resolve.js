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
  const updated = source
    .replace('catch (err) {', 'catch (_err) {')
    .replace(
      '_storeResult(strPath, /** @type {Error} */ (err), undefined)',
      '_storeResult(strPath, /** @type {Error} */ (_err), undefined)',
    )
    .replace(
      'runCallbacks(callbacks, /** @type {Error} */ (err), undefined)',
      'runCallbacks(callbacks, /** @type {Error} */ (_err), undefined)',
    )
    .replace('throw err;', 'throw _err;');

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
