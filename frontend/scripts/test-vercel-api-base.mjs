import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const validator = fileURLToPath(new URL('./validate-vercel-api-base.mjs', import.meta.url));

function validate(value) {
  try {
    execFileSync(process.execPath, [validator], {
      env: { ...process.env, VITE_API_URL: value },
      stdio: 'pipe',
    });
    return true;
  } catch {
    return false;
  }
}

test('Vercel uses the same-origin gateway', () => {
  assert.equal(validate('/api'), true);
});

test('Vercel rejects browser loopback and external API origins', () => {
  assert.equal(validate('http://localhost:8080'), false);
  assert.equal(validate('http://127.0.0.1:18000'), false);
  assert.equal(validate('https://tracera.pheno.studio/api'), false);
});
