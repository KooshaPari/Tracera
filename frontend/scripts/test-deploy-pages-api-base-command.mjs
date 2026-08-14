import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import test from 'node:test'

const workflow = fileURLToPath(
  new URL('../../.github/workflows/deploy-pages.yml', import.meta.url),
)

test('Pages validates the production API base from the frontend workspace root', () => {
  const source = readFileSync(workflow, 'utf8')

  assert.match(
    source,
    /PRODUCTION_DEPLOY=1 npm --prefix "\$GITHUB_WORKSPACE\/frontend" run test:api-base/,
  )
})
