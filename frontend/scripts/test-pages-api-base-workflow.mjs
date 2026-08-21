import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const workflow = readFileSync('.github/workflows/deploy-pages.yml', 'utf8');
const buildStep = workflow.match(
  /- name: Build frontend([\s\S]*?)(?=\n      - name:|\n  [A-Za-z])/,
);

assert.ok(buildStep, 'Pages workflow must define a Build frontend step');
assert.match(
  buildStep[1],
  /working-directory: frontend\/apps\/web/,
  'Pages build must run from the web workspace',
);
assert.match(
  buildStep[1],
  /npm --prefix \.\.\/\.\. run test:api-base/,
  'Pages must invoke the root frontend test script from the web workspace',
);
assert.doesNotMatch(
  buildStep[1],
  /npm run test:api-base/,
  'Pages must not resolve test:api-base from the web package',
);
