#!/usr/bin/env node

// Verifies the deployed backend still exposes the routes the frontend calls.
//
// A healthy deployment guards almost all of these: /health and /readyz are
// public, while the data routes require a bearer token. An unauthenticated CI
// run therefore cannot receive a 2xx from them, and 401/403 is the correct
// answer - it proves the route exists and is protected. Only a 404 (route gone)
// or a 5xx (server broken) means the deployment is out of alignment, so this
// script classifies by status instead of demanding 200 from every path.

const base = process.env.VITE_API_URL || 'http://127.0.0.1:8080'
const endpoints = [
  '/health',
  '/readyz',
  '/sdlc-pm/sprints',
  '/org-intel/teams',
  '/org-intel/metrics',
  '/evidence',
]

// Routes that require a bearer token on a real deployment.
const AUTH_GATED = new Set([
  '/sdlc-pm/sprints',
  '/org-intel/teams',
  '/org-intel/metrics',
  '/evidence',
])

async function request(path) {
  const response = await fetch(`${base}${path}`)
  const text = await response.text()
  const guarded = AUTH_GATED.has(path) && (response.status === 401 || response.status === 403)
  if (!response.ok && !guarded) {
    throw new Error(`${path}: ${response.status} ${response.statusText}: ${text || 'empty'}`)
  }
  return { guarded, payload: guarded || !text ? {} : JSON.parse(text) }
}

try {
  const failures = []
  for (const path of endpoints) {
    try {
      const { guarded, payload } = await request(path)

      if (guarded) {
        console.log(`OK ${path} (route present, requires authentication)`)
        continue
      }

      const isArrayPayload = Array.isArray(payload)
      if (path === '/evidence' && !(Array.isArray(payload?.items) || Number.isInteger(payload?.count))) {
        throw new Error('evidence response must include items/count')
      }

      if ((path === '/sdlc-pm/sprints' || path === '/org-intel/teams') && !isArrayPayload) {
        throw new Error('expected JSON array')
      }

      if (path === '/org-intel/metrics' && !payload) {
        throw new Error('expected metrics object')
      }

      console.log(`OK ${path}`)
    } catch (err) {
      failures.push(err.message)
      console.error(`FAIL ${path}: ${err.message}`)
    }
  }

  if (failures.length > 0) {
    console.error(`\nSmoke check failed with ${failures.length} endpoint failure(s).`)
    process.exit(1)
  }

  console.log('\nTracera frontend backend alignment smoke: PASS')
} catch (err) {
  console.error(err)
  process.exitCode = 1
}
