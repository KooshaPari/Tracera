const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { mkdtempSync, mkdirSync, rmSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');
const test = require('node:test');

const repoRoot = join(__dirname, '..');
const cli = join(repoRoot, 'bin', 'tracera');

function config(env) {
  return JSON.parse(execFileSync(process.execPath, [cli, 'config'], {
    cwd: repoRoot,
    encoding: 'utf8',
    env: { ...process.env, ...env },
  }));
}

test('uses the rich loopback gateway by default', () => {
  const home = mkdtempSync(join(tmpdir(), 'tracera-cli-default-'));
  try {
    const result = config({ HOME: home, TRACERA_API_BASE: '' });
    assert.equal(result.apiBase, 'http://127.0.0.1:18000');
    assert.equal(result.source, 'default');
  } finally {
    rmSync(home, { recursive: true, force: true });
  }
});

test('keeps flag, environment, and file precedence', () => {
  const home = mkdtempSync(join(tmpdir(), 'tracera-cli-precedence-'));
  try {
    mkdirSync(join(home, '.tracera'));
    writeFileSync(join(home, '.tracera', 'config.json'), JSON.stringify({
      apiBase: 'http://127.0.0.1:19000',
    }));
    const fileResult = config({ HOME: home, TRACERA_API_BASE: '' });
    assert.equal(fileResult.apiBase, 'http://127.0.0.1:19000');
    assert.equal(fileResult.source, 'file');
    assert.equal(
      config({ HOME: home, TRACERA_API_BASE: 'http://127.0.0.1:19001' }).apiBase,
      'http://127.0.0.1:19001'
    );
    const result = JSON.parse(execFileSync(process.execPath, [cli, 'config', '--api-base',
      'http://127.0.0.1:19002'], {
      cwd: repoRoot,
      encoding: 'utf8',
      env: { ...process.env, HOME: home, TRACERA_API_BASE: 'http://127.0.0.1:19001' },
    }));
    assert.equal(result.apiBase, 'http://127.0.0.1:19002');
    assert.equal(result.source, 'flag');
  } finally {
    rmSync(home, { recursive: true, force: true });
  }
});
