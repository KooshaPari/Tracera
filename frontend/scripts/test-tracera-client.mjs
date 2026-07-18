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
    const pathname = url.replace('http://localhost:8080', '');

    if (routeMap[pathname]) {
      return routeMap[pathname]();
    }

    throw new Error(`Unexpected route: ${pathname}`);
  };
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

await runCase('getHealth happy path', async () => {
  global.fetch = createResponseResolver({
    '/health': () => makeResponse({ body: { status: 'ok' } }),
    '/sdlc-pm/sprints': () => makeResponse({ body: [{ id: 'S1', status: 'active' }] }),
    '/org-intel/teams': () => makeResponse({ body: [{ id: 'T1', name: 'core' }] }),
    '/org-intel/metrics': () =>
      makeResponse({
        body: { total_artifacts: 5, coverage_ratio: 0.82, open_gaps: 1 },
      }),
    '/evidence': () => makeResponse({ body: { count: 2, items: [{ id: 1 }, { id: 2 }] } }),
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
});

await runCase('non-JSON evidence fallback to count default', async () => {
  global.fetch = createResponseResolver({
    '/health': () => makeResponse({ body: { status: 'ok' } }),
    '/sdlc-pm/sprints': () => makeResponse({ body: [] }),
    '/org-intel/teams': () => makeResponse({ body: [] }),
    '/org-intel/metrics': () => makeResponse({ body: { total_artifacts: 1, coverage_ratio: 0.5, open_gaps: 0 } }),
    '/evidence': () => makeResponse({
      headers: { 'content-type': 'text/plain' },
      body: {},
    }),
  });

  const evidence = await traceraClient.getEvidence();
  assert.equal(evidence.count, 0);
  assert.deepEqual(evidence.items, []);
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
});

console.log('traceraClient tests complete');
