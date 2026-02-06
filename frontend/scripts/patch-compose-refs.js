#!/usr/bin/env node
/**
 * Patch @radix-ui/react-compose-refs to defer function ref invocation to queueMicrotask.
 * Fixes "Maximum update depth exceeded" when a composed ref callback calls setState during React commit (e.g. React 19 + Radix TabsTrigger/CollapsibleTrigger).
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const targetPath = path.join(
  __dirname,
  '..',
  'node_modules',
  '@radix-ui',
  'react-compose-refs',
  'dist',
  'index.mjs',
);

const altPath = path.join(
  __dirname,
  '..',
  '..',
  'node_modules',
  '@radix-ui',
  'react-compose-refs',
  'dist',
  'index.mjs',
);

const MARKER = 'queueMicrotask';
const ORIGINAL = `function setRef(ref, value) {
	if (typeof ref === "function") {
		return ref(value);
	} else if (ref !== null && ref !== void 0) {
		ref.current = value;
	}
}`;
const PATCHED = `function setRef(ref, value) {
	if (typeof ref === "function") {
		// Defer function ref to avoid setState during React commit (fixes "Maximum update depth" with React 19)
		let cancelled = false;
		let cleanupFn;
		queueMicrotask(() => {
			if (cancelled) return;
			cleanupFn = ref(value);
		});
		return () => {
			cancelled = true;
			if (typeof cleanupFn === "function") cleanupFn();
			else ref(null);
		};
	} else if (ref !== null && ref !== void 0) {
		ref.current = value;
	}
}`;

function patch(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  if (content.includes(MARKER)) {
    return;
  }
  if (!content.includes('return ref(value);')) {
    return;
  }
  content = content.replace(ORIGINAL, PATCHED);
  fs.writeFileSync(filePath, content);
}

const pathToPatch = fs.existsSync(targetPath) ? targetPath : altPath;
if (fs.existsSync(pathToPatch)) {
  patch(pathToPatch);
}
