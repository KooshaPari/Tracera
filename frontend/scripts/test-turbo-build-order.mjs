#!/usr/bin/env node
/** Verify every web build task waits for workspace dependency builds. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const scriptsDir = path.dirname(fileURLToPath(import.meta.url));
const turboConfigPath = path.resolve(scriptsDir, '..', 'turbo.json');
const turboConfig = JSON.parse(fs.readFileSync(turboConfigPath, 'utf8'));

for (const taskName of ['build', 'build:fast']) {
  test(`${taskName} waits for workspace dependency builds`, () => {
    const dependsOn = turboConfig.tasks[taskName]?.dependsOn;
    assert.ok(Array.isArray(dependsOn), `${taskName} must declare dependsOn`);
    assert.ok(
      dependsOn.includes('^build'),
      `${taskName} must include ^build so declarations exist before dependents compile`,
    );
  });
}
