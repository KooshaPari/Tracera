import assert from 'node:assert/strict'
import test from 'node:test'

import {
  buildApiUrl,
  loadDashboardData,
  normalizeApiBase,
  resolveApiConfiguration,
} from './api.js'

test('blank API configuration uses same-origin relative URLs', () => {
  assert.equal(normalizeApiBase(undefined), '')
  assert.equal(normalizeApiBase('  '), '')
  assert.equal(buildApiUrl('', '/health'), '/health')
})

test('configured API origin is trimmed and has trailing slashes removed', () => {
  assert.equal(
    normalizeApiBase('  https://api.tracera.example///  '),
    'https://api.tracera.example',
  )
  assert.equal(
    buildApiUrl('https://api.tracera.example', '/health'),
    'https://api.tracera.example/health',
  )
})

test('invalid API origins fail with a visible configuration diagnostic', () => {
  assert.throws(
    () => normalizeApiBase('file:///tmp/tracera.sock'),
    /VITE_API_BASE must be an http\(s\) origin or a root-relative path/,
  )
})

test('invalid API configuration resolves to a renderable diagnostic', () => {
  assert.deepEqual(resolveApiConfiguration('file:///tmp/tracera.sock'), {
    apiBase: '',
    error: 'VITE_API_BASE must be an http(s) origin or a root-relative path',
  })
})

test('same-origin API configuration resolves without a diagnostic', () => {
  assert.deepEqual(resolveApiConfiguration(undefined), {
    apiBase: '',
    error: null,
  })
})

test('dashboard loading preserves successes and reports every failed endpoint', async () => {
  const responses = new Map([
    ['/health', { ok: true, status: 200, body: { status: 'ok' } }],
    ['/sdlc-pm/sprints', { ok: false, status: 503, body: null }],
    ['/org-intel/teams', { ok: true, status: 200, body: [{ id: 'platform' }] }],
  ])

  const fetchImpl = async (url) => {
    const response = responses.get(url)
    assert.ok(response, `unexpected request: ${url}`)
    return {
      ok: response.ok,
      status: response.status,
      json: async () => response.body,
    }
  }

  const result = await loadDashboardData('', fetchImpl)

  assert.deepEqual(result.health, { status: 'ok' })
  assert.deepEqual(result.teams, [{ id: 'platform' }])
  assert.deepEqual(result.sprints, [])
  assert.deepEqual(result.failures, [
    {
      endpoint: '/sdlc-pm/sprints',
      message: 'HTTP 503',
    },
  ])
})

test('network failures are reported with endpoint context', async () => {
  const fetchImpl = async (url) => {
    if (url === '/health') {
      throw new TypeError('Failed to fetch')
    }
    return {
      ok: true,
      status: 200,
      json: async () => [],
    }
  }

  const result = await loadDashboardData('', fetchImpl)

  assert.deepEqual(result.failures, [
    {
      endpoint: '/health',
      message: 'Failed to fetch',
    },
  ])
})
