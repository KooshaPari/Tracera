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

  let tokenRequests = 0
  const getAccessToken = async () => {
    tokenRequests += 1
    return 'test-access-token'
  }
  const fetchImpl = async (url, options) => {
    const response = responses.get(url)
    assert.ok(response, `unexpected request: ${url}`)
    assert.equal(options.headers.Authorization, 'Bearer test-access-token')
    return {
      ok: response.ok,
      status: response.status,
      json: async () => response.body,
    }
  }

  const result = await loadDashboardData('', getAccessToken, fetchImpl)

  assert.equal(tokenRequests, 1)
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
  const fetchImpl = async (url, options) => {
    assert.equal(options.headers.Authorization, 'Bearer test-access-token')
    if (url === '/health') {
      throw new TypeError('Failed to fetch')
    }
    return {
      ok: true,
      status: 200,
      json: async () => [],
    }
  }

  const result = await loadDashboardData(
    '',
    async () => 'test-access-token',
    fetchImpl,
  )

  assert.deepEqual(result.failures, [
    {
      endpoint: '/health',
      message: 'Failed to fetch',
    },
  ])
})

test('token acquisition failure is visible and prevents API requests', async () => {
  let requestCount = 0
  const fetchImpl = async () => {
    requestCount += 1
    throw new Error('API request should not run')
  }

  await assert.rejects(
    () =>
      loadDashboardData(
        '',
        async () => {
          throw new Error('session expired')
        },
        fetchImpl,
      ),
    /Unable to authenticate API requests: session expired/,
  )
  assert.equal(requestCount, 0)
})

test('missing access token is visible and prevents API requests', async () => {
  await assert.rejects(
    () => loadDashboardData('', async () => undefined, async () => undefined),
    /WorkOS returned no access token/,
  )
})
