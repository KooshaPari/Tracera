import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import test from 'node:test'

const script = fileURLToPath(new URL('./validate-api-base.mjs', import.meta.url))
const http = ['http', '://'].join('')

function run(raw, extra = {}) {
  try {
    execFileSync(process.execPath, [script], {
      env: { ...process.env, VITE_API_URL: raw, ...extra },
      stdio: 'pipe',
    })
    return { ok: true, output: '' }
  } catch (error) {
    return { ok: false, output: `${error.stdout || ''}${error.stderr || ''}` }
  }
}

test('accepts IPv4 and expanded IPv6 loopback over HTTP', () => {
  assert.equal(run(`${http}127.0.0.1:8080`).ok, true)
  assert.equal(run(`${http}[0:0:0:0:0:0:0:1]:8080`).ok, true)
  assert.equal(run(`${http}[::ffff:127.0.0.1]:8080`).ok, true)
})

test('reports malformed API bases clearly', () => {
  const result = run('not a URL')
  assert.equal(result.ok, false)
  assert.match(result.output, /invalid API base URL/)
})

test('still rejects insecure non-loopback bases', () => {
  const result = run(`${http}api.example.com`)
  assert.equal(result.ok, false)
  assert.match(result.output, /refusing insecure non-loopback API base/)
})

test('uses VITE_API_URL as the canonical variable', () => {
  const result = run('https://api.example.com', { VITE_API_BASE: 'not a URL', PRODUCTION_DEPLOY: '1' })
  assert.equal(result.ok, true)
})
