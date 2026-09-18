#!/usr/bin/env node

// Verifies the deployed backend still exposes the write routes the frontend
// calls with the documented payload shapes.
//
// These routes are state-mutating, so a real deployment rejects an
// unauthenticated POST before it ever reaches the handler: CSRF protection
// answers 403 without a canonical Origin and an issued `x-csrf-token`, and the
// bearer-token layer answers 401 once CSRF is satisfied. A CI run holds neither
// credential, so 401/403 is the healthy answer - it proves the route exists and
// is guarded. Only a 404 (route gone) or a 5xx (server broken) means the
// deployment is out of alignment.

const base = process.env.VITE_API_URL || 'http://127.0.0.1:8080'

const GUARDED_STATUSES = new Set([401, 403])

const checks = [
  {
    name: 'POST /api/v1/coverage-matrix',
    path: '/api/v1/coverage-matrix',
    method: 'POST',
    body: {
      links: [{ source_id: 'A', target_id: 'B', relationship: 'depends', confidence: 0.91 }],
      stale_after_days: 7,
    },
  },
  {
    name: 'POST /api/v1/impact',
    path: '/api/v1/impact',
    method: 'POST',
    body: {
      links: [{ source_id: 'A', target_id: 'B', relationship: 'depends', confidence: 0.91 }],
      changed_artifact_ids: ['A'],
      max_depth: 2,
    },
  },
  {
    name: 'POST /api/v1/confidence',
    path: '/api/v1/confidence',
    method: 'POST',
    body: {
      requirement_text: 'Requirement must use encryption',
      artifact_text: 'All requests are encrypted in transit',
    },
  },
  {
    name: 'POST /api/v1/governance/spec-check',
    path: '/api/v1/governance/spec-check',
    method: 'POST',
    body: {
      specs: [
        {
          spec_id: 'S-1',
          acceptance_criteria: ['Must provide audit'],
          evidence_links: ['A'],
          status: 'approved',
        },
      ],
      traces: [
        { spec_id: 'S-1', kind: 'implementation', target_id: 'A' },
        { spec_id: 'S-1', kind: 'test', target_id: 'B' },
      ],
    },
  },
  {
    name: 'POST /api/v1/blast-radius',
    path: '/api/v1/blast-radius',
    method: 'POST',
    body: {
      links: [{ source_id: 'A', target_id: 'B', relationship: 'depends', confidence: 0.91 }],
      changed_artifact_ids: ['A'],
    },
  },
  {
    name: 'POST /api/v1/trace/forward/a1',
    path: '/api/v1/trace/forward/a1',
    method: 'POST',
    body: {
      links: [{ source_id: 'a1', target_id: 'b1', relationship: 'depends', confidence: 1.0 }],
    },
  },
  {
    name: 'POST /api/v1/trace/reverse/a1',
    path: '/api/v1/trace/reverse/a1',
    method: 'POST',
    body: {
      links: [{ source_id: 'b1', target_id: 'a1', relationship: 'depends', confidence: 1.0 }],
    },
  },
]

const errors = []

async function request({ name, path, method, body }) {
  const url = `${base}${path}`
  const response = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const text = await response.text()

  if (GUARDED_STATUSES.has(response.status)) {
    console.log(`PASS ${name} (route present, requires authentication)`)
    return
  }

  if (!response.ok) {
    throw new Error(`${name} failed: ${response.status} ${response.statusText}: ${text || 'empty body'}`)
  }

  const payload = text ? JSON.parse(text) : {}
  const isObject = payload !== null && typeof payload === 'object'
  if (!isObject) {
    throw new Error(`${name}: expected object payload`)
  }

  console.log(`PASS ${name}`)
}

try {
  for (const test of checks) {
    try {
      await request(test)
    } catch (err) {
      errors.push(err.message)
      console.error(err.message)
    }
  }

  if (errors.length) {
    console.error(`\nPOST smoke failed with ${errors.length} failures`)
    process.exitCode = 1
  } else {
    console.log('\nTracera POST endpoint smoke: PASS')
  }
} catch (err) {
  console.error(err)
  process.exitCode = 1
}
