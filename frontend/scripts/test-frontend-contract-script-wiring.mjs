import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const rootPackage = JSON.parse(readFileSync('frontend/package.json', 'utf8'))
assert.equal(
  rootPackage.scripts?.['test:a11y'],
  'bun --cwd apps/web run test:a11y',
  'frontend root must forward test:a11y to the web workspace',
)
