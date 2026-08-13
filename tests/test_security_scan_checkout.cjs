const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const test = require('node:test');

const workflow = readFileSync(
  join(__dirname, '..', '.github', 'workflows', 'ci.yml'),
  'utf8'
);

test('Security Scan checks out full history before gitleaks', () => {
  const securityJob = workflow.match(/  security:\n([\s\S]*?)(?=\n  [\w-]+:|\n?$)/);
  assert.ok(securityJob, 'Security Scan job must exist');
  assert.match(
    securityJob[1],
    /- uses: actions\/checkout@v4\n        with:\n          fetch-depth: 0\n      - name: gitleaks/
  );
});
