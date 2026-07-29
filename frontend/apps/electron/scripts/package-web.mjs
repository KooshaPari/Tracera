import { cp, mkdir, access, rm } from 'node:fs/promises';
import { constants } from 'node:fs';
import { join, resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
// apps/web writes to frontend/dist (see its Vite outDir), not apps/web/dist.
const source = resolve(root, '../../dist');
const destination = resolve(root, 'dist/web');

try {
  await access(join(source, 'index.html'), constants.R_OK);
} catch {
  throw new Error(`canonical rich SPA is not built: ${source}/index.html; run 'bun --cwd ../web run build' first`);
}
await rm(destination, { recursive: true, force: true });
await mkdir(destination, { recursive: true });
await cp(source, destination, { recursive: true });
console.log(`Packaged canonical rich SPA: ${source} -> ${destination}`);
