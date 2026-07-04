import fs from 'node:fs';
import path from 'node:path';

const roots = [
  path.resolve('node_modules/next/dist'),
  path.resolve('apps/docs/node_modules/next/dist'),
];

const isJsFile = (filePath) => filePath.endsWith('.js');

const countBraces = (text) => {
  let count = 0;
  for (const ch of text) {
    if (ch === '{') count += 1;
    if (ch === '}') count -= 1;
  }
  return count;
};

const patchFile = (filePath) => {
  const original = fs.readFileSync(filePath, 'utf8');
  if (!original.includes('catch (_err)') && !original.includes('catch(_err)')) {
    return false;
  }
  if (!/\berr\b/.test(original)) {
    return false;
  }
  const lines = original.split('\n');
  let updated = false;
  let inCatch = false;
  let braceDepth = 0;

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (!inCatch && (line.includes('catch (_err)') || line.includes('catch(_err)'))) {
      inCatch = true;
      const catchIndex = line.indexOf('catch');
      const afterCatch = catchIndex === -1 ? line : line.slice(catchIndex);
      braceDepth = countBraces(afterCatch);
    }

    if (inCatch) {
      const patchedLine = line.replace(/\berr\b/g, '_err');
      if (patchedLine !== line) {
        lines[i] = patchedLine;
        updated = true;
      }
      braceDepth += countBraces(line);
      if (braceDepth <= 0) {
        inCatch = false;
        braceDepth = 0;
      }
    }
  }

  if (updated) {
    fs.writeFileSync(filePath, lines.join('\n'), 'utf8');
  }
  return updated;
};

const walk = (dirPath, onFile) => {
  if (!fs.existsSync(dirPath)) return;
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath, onFile);
    } else if (entry.isFile() && isJsFile(fullPath)) {
      onFile(fullPath);
    }
  }
};

let patchedCount = 0;
for (const root of roots) {
  walk(root, (filePath) => {
    if (patchFile(filePath)) {
      patchedCount += 1;
    }
  });
}

if (patchedCount > 0) {
  console.log(`[patch-next-document] patched ${patchedCount} file(s) under next/dist`);
}
