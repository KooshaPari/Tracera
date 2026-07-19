#!/usr/bin/env node
import assert from 'node:assert/strict';
import { traceraClient } from '../apps/web/src/services/traceraClient.js';

function makeHeaders(value) {
  return {
    get(name) {
      return value[name.toLowerCase()] || value[name] || null;
    },
  };
}

function makeResponse({
  ok = true,
  status = 200,
  statusText = 'OK',
  headers = { 'content-type': 'application/json' },
  body = {},
}) {
  return {
    ok,
    status,
    statusText,
    headers: makeHeaders(headers),
    async json() {
      return body;
    },
  };
}

function createResponseResolver(routeMap) {
  return async function fetchMock(input) {
    const url = String(input);
    // Resolve the path independently of the configured loopback host. This
    // keeps the contract test valid for localhost, 127.0.0.1, IPv6 loopback,
    // and CI-injected VITE_API_BASE values.
    const pathname = new URL(url).pathname;

    if (routeMap[pathname]) {
      return routeMap[pathname]();
    }

    throw new Error(`Unexpected route: ${pathname}`);
  };
}

function makeLink() {
  return { source_id: 'a', target_id: 'b', relationship: 'depends', confidence: 1.0 };
}

async function runCase(name, fn) {
  try {
    await fn();
    console.log(`PASS ${name}`);
  } catch (error) {
    console.error(`FAIL ${name}`, error.message);
    process.exitCode = 1;
  }
}

await runCase('traceraClient happy path (GET + POST contracts)', async () => {
  global.fetch = createResponseResolver({
    '/health': () => makeResponse({ body: { status: 'ok' } }),
    '/sdlc-pm/sprints': () => makeResponse({ body: [{ id: 'S1', status: 'active' }] }),
    '/org-intel/teams': () => makeResponse({ body: [{ id: 'T1', name: 'core' }] }),
    '/org-intel/metrics': () =>
      makeResponse({
        body: { total_artifacts: 5, coverage_ratio: 0.82, open_gaps: 1 },
      }),
    '/evidence': () => makeResponse({ body: { count: 2, items: [{ id: 1 }, { id: 2 }] } }),
    '/api/v1/coverage-matrix': () =>
      makeResponse({
        body: {
          generated_at: '2026-07-18T00:00:00Z',
          link_count: 1,
          cell_count: 0,
          stale_links: 0,
          cells: [],
        },
      }),
    '/api/v1/impact': () =>
      makeResponse({
        body: {
          seeds: ['a'],
          affected: [{ artifact_id: 'a', depth: 0, via: [], score: 1.0 }],
          total_score: 1.0,
          truncated: false,
          max_depth_seen: 1,
          conflicts: [],
        },
      }),
    '/api/v1/confidence': () => makeResponse({ body: { confidence: 0.65, rationale: 'mock' } }),
    '/api/v1/governance/spec-check': () =>
      makeResponse({
        body: { status: 'pass', spec_count: 1, trace_count: 1, violations: [] },
      }),
    '/api/v1/blast-radius': () =>
      makeResponse({
        body: { seeds: ['a'], blast_radius: [], total: 1 },
      }),
    '/api/v1/trace/forward/a1': () =>
      makeResponse({ body: { artifact_id: 'a1', direction: 'forward', neighbors: ['a2'] } }),
    '/api/v1/trace/reverse/a1': () =>
      makeResponse({ body: { artifact_id: 'a1', direction: 'reverse', neighbors: [] } }),
  });

  const health = await traceraClient.getHealth();
  assert.deepEqual(health, { status: 'ok' });

  const sprints = await traceraClient.getSprints();
  assert.equal(sprints.length, 1);
  assert.equal(sprints[0].id, 'S1');

  const teams = await traceraClient.getTeams();
  assert.equal(teams[0].name, 'core');

  const metrics = await traceraClient.getMetrics();
  assert.equal(metrics.total_artifacts, 5);

  const evidence = await traceraClient.getEvidence();
  assert.equal(evidence.count, 2);
  assert.equal(evidence.items.length, 2);

  const matrix = await traceraClient.postCoverageMatrix({
    links: [makeLink()],
    stale_after_days: 7,
  });
  assert.equal(matrix.link_count, 1);

  const impact = await traceraClient.postImpact({
    links: [makeLink()],
    changed_artifact_ids: ['a'],
    max_depth: 2,
  });
  assert.equal(impact.total_score, 1.0);

  const confidence = await traceraClient.postConfidence({
    requirement_text: 'req',
    artifact_text: 'artifact',
  });
  assert.equal(typeof confidence.confidence, 'number');

  const specCheck = await traceraClient.postSpecCheck({
    specs: [{ spec_id: 'S1', acceptance_criteria: ['ok'], evidence_links: ['a'], status: 'approved' }],
    traces: [{ spec_id: 'S1', kind: 'implementation', target_id: 't1' }],
  });
  assert.equal(specCheck.status, 'pass');

  const blast = await traceraClient.postBlastRadius({
    links: [makeLink()],
    changed_artifact_ids: ['a'],
  });
  assert.ok(Array.isArray(blast.blast_radius));

  const forward = await traceraClient.postTraceForward('a1', {
    links: [{ source_id: 'a1', target_id: 'a2', relationship: 'depends', confidence: 1.0 }],
  });
  assert.equal(forward.direction, 'forward');
  assert.equal(forward.artifact_id, 'a1');

  const reverse = await traceraClient.postTraceReverse('a1', {
    links: [{ source_id: 'a2', target_id: 'a1', relationship: 'depends', confidence: 1.0 }],
  });
  assert.equal(reverse.direction, 'reverse');
});

await runCase('non-JSON evidence fallback to count default', async () => {
  global.fetch = createResponseResolver({
    '/health': () => makeResponse({ body: { status: 'ok' } }),
    '/sdlc-pm/sprints': () => makeResponse({ body: [] }),
    '/org-intel/teams': () => makeResponse({ body: [] }),
    '/org-intel/metrics': () =>
      makeResponse({ body: { total_artifacts: 1, coverage_ratio: 0.5, open_gaps: 0 } }),
    '/evidence': () =>
      makeResponse({
        headers: { 'content-type': 'text/plain' },
        body: { count: 0, items: [] },
      }),
    '/api/v1/coverage-matrix': () => makeResponse({ body: {} }),
    '/api/v1/impact': () => makeResponse({ body: {} }),
    '/api/v1/confidence': () => makeResponse({ body: {} }),
    '/api/v1/governance/spec-check': () => makeResponse({ body: {} }),
    '/api/v1/blast-radius': () => makeResponse({ body: {} }),
    '/api/v1/trace/forward/a1': () => makeResponse({ body: {} }),
    '/api/v1/trace/reverse/a1': () => makeResponse({ body: {} }),
  });

  const evidence = await traceraClient.getEvidence();
  assert.equal(evidence.count ?? 0, 0);
  assert.deepEqual(evidence.items, []);

  const matrix = await traceraClient.postCoverageMatrix();
  assert.equal(typeof matrix, 'object');
  const impact = await traceraClient.postImpact();
  assert.equal(impact.total_score, 0.0);
});

await runCase('HTTP error surfaces status/body message', async () => {
  global.fetch = createResponseResolver({
    '/health': () =>
      makeResponse({
        ok: false,
        status: 500,
        statusText: 'Server Error',
        body: { error: 'boom' },
      }),
    '/sdlc-pm/sprints': () => makeResponse({ body: [] }),
    '/org-intel/teams': () => makeResponse({ body: [] }),
    '/org-intel/metrics': () => makeResponse({ body: {} }),
    '/evidence': () => makeResponse({ body: { count: 1, items: [] } }),
    '/api/v1/coverage-matrix': () =>
      makeResponse({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        body: { error: 'bad' },
      }),
  });

  await assert.rejects(
    () => traceraClient.getHealth(),
    (error) => {
      assert.match(error.message, /500/);
      assert.match(error.message, /Server Error/);
      assert.match(error.message, /boom/);
      return true;
    },
  );

  await assert.rejects(
    () => traceraClient.postCoverageMatrix(),
    (error) => {
      assert.match(error.message, /400/);
      assert.match(error.message, /Bad Request/);
      assert.match(error.message, /bad/);
      return true;
    },
  );
});

await runCase('request timeout aborts stalled fetch deterministically', async () => {
  global.fetch = async (_url, options) => await new Promise((_resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(new Error('aborted by signal')), { once: true });
  });

  await assert.rejects(
    () => traceraClient.getHealth({ timeoutMs: 5 }),
    (error) => {
      assert.equal(error.message, 'Request timed out after 5ms');
      return true;
    },
  );
});

console.log('traceraClient tests complete');
