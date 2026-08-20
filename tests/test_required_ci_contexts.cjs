const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const test = require('node:test');

const workflow = readFileSync(
  join(__dirname, '..', '.github', 'workflows', 'ci.yml'),
  'utf8',
);

function jobBlock(jobId) {
  const match = workflow.match(
    new RegExp(`^  ${jobId}:\\n([\\s\\S]*?)(?=^  [A-Za-z0-9_-]+:|\\z)`, 'm'),
  );
  assert.ok(match, `expected ${jobId} aggregate job`);
  return match[0];
}

function assertAggregateJob({ jobId, context, needs }) {
  const block = jobBlock(jobId);
  assert.match(block, new RegExp(`^    name: ${context}$`, 'm'));
  assert.match(block, /^    if: always\(\)$/m);

  for (const dependency of needs) {
    assert.match(block, new RegExp(`^      - ${dependency}$`, 'm'));
  }
}

test('CI emits the protected lint and test contexts across all merge entrypoints', () => {
  assert.match(workflow, /^  push:/m);
  assert.match(workflow, /^  pull_request:/m);
  assert.match(workflow, /^  merge_group:/m);

  assertAggregateJob({
    jobId: 'required-ci-lint',
    context: 'ci / lint',
    needs: ['rust-lint', 'python-lint', 'go-lint', 'typescript-lint', 'trunk-check'],
  });
  assertAggregateJob({
    jobId: 'required-ci-test',
    context: 'ci / test',
    needs: ['rust-test', 'python-test', 'go-test', 'typescript-test'],
  });
});
