import { describe, expect, expectTypeOf, it, vi } from 'vitest';
import { TraceraApiClient, fetchCoverageMatrix } from './index.js';
import type {
  ConfidenceRequest,
  ConfidenceResponse,
  CoverageMatrixRequest,
  CoverageMatrixResponse,
  EvidenceCreate,
  EvidenceResponse,
  GovernanceCheckRequest,
  GovernanceReport,
  ImpactRequest,
  ImpactResponse,
} from '@tracertm/types';

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
}

describe('fetchCoverageMatrix', () => {
  it('posts a typed CoverageMatrixRequest and resolves with a CoverageMatrixResponse', async () => {
    const responseBody: CoverageMatrixResponse = {
      generated_at: '2026-06-16T00:00:00Z',
      link_count: 1,
      cell_count: 1,
      stale_links: 0,
      cells: [
        {
          source_id: 'req-1',
          target_id: 'code-1',
          coverage: 'covered',
          links: [
            {
              source_id: 'req-1',
              target_id: 'code-1',
              relationship: 'satisfies',
              confidence: 1.0,
            },
          ],
        },
      ],
    };

    const fetchImpl = vi.fn(
      async () =>
        new Response(JSON.stringify(responseBody), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
    );

    const request: CoverageMatrixRequest = {
      links: [{ source_id: 'req-1', target_id: 'code-1', relationship: 'satisfies' }],
      stale_after_days: 30,
    };

    const result = await fetchCoverageMatrix('https://api.example.test/', request, fetchImpl as unknown as typeof fetch);

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    const firstCall = fetchImpl.mock.calls[0] as unknown as [string, RequestInit];
    const [calledUrl, calledInit] = firstCall;
    expect(calledUrl).toBe('https://api.example.test/api/v1/coverage-matrix');
    expect(calledInit.method).toBe('POST');
    expect(JSON.parse(calledInit.body as string)).toEqual(request);
    expect(result).toEqual(responseBody);

    // Type assertions: the resolved value must match CoverageMatrixResponse,
    // and the request parameter must accept the full typed shape.
    expectTypeOf(result).toEqualTypeOf<CoverageMatrixResponse>();
    expectTypeOf(request).toMatchTypeOf<CoverageMatrixRequest>();
  });
});

describe('TraceraApiClient', () => {
  function makeClient(handler: (url: string, init: RequestInit) => Response) {
    const fetchImpl = vi.fn(
      async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = typeof input === 'string' ? input : input.toString();
        return handler(url, init ?? {});
      },
    );
    const client = new TraceraApiClient({
      baseUrl: 'https://api.example.test/',
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    return { client, fetchImpl };
  }

  it('buildCoverageMatrix POSTs to /api/v1/coverage-matrix', async () => {
    const body: CoverageMatrixResponse = {
      generated_at: '2026-06-16T00:00:00Z',
      link_count: 1,
      cell_count: 1,
      stale_links: 0,
      cells: [],
    };
    const { client, fetchImpl } = makeClient(() => jsonResponse(body));
    const request: CoverageMatrixRequest = {
      links: [{ source_id: 'r', target_id: 'c', relationship: 'satisfies' }],
    };

    const result = await client.buildCoverageMatrix(request);

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('https://api.example.test/api/v1/coverage-matrix');
    expect(init.method).toBe('POST');
    expect(JSON.parse(init.body as string)).toEqual(request);
    expect(result).toEqual(body);
    expectTypeOf(result).toEqualTypeOf<CoverageMatrixResponse>();
  });

  it('analyzeImpact POSTs to /api/v1/impact', async () => {
    const body: ImpactResponse = {
      seeds: ['c-1'],
      affected: [{ artifact_id: 't-1', depth: 1, via: ['verifies'], score: 0.75 }],
      total_score: 0.75,
      truncated: false,
      max_depth_seen: 1,
      conflicts: [],
    };
    const { client, fetchImpl } = makeClient(() => jsonResponse(body));
    const request: ImpactRequest = {
      changed_artifact_ids: ['c-1'],
      max_depth: 3,
      links: [],
    };

    const result = await client.analyzeImpact(request);

    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('https://api.example.test/api/v1/impact');
    expect(init.method).toBe('POST');
    expect(JSON.parse(init.body as string)).toEqual(request);
    expect(result).toEqual(body);
    expectTypeOf(result).toEqualTypeOf<ImpactResponse>();
  });

  it('specCheck POSTs to /api/v1/governance/spec-check', async () => {
    const body: GovernanceReport = {
      status: 'pass',
      spec_count: 1,
      trace_count: 2,
      violations: [],
    };
    const { client, fetchImpl } = makeClient(() => jsonResponse(body));
    const request: GovernanceCheckRequest = {
      specs: [
        {
          spec_id: 's-1',
          title: 'Spec',
          owner: 'koosh',
          acceptance_criteria: ['a'],
          evidence_links: ['e'],
          status: 'approved',
        },
      ],
      traces: [
        { spec_id: 's-1', target_id: 'c-1', kind: 'implementation' },
        { spec_id: 's-1', target_id: 't-1', kind: 'test' },
      ],
    };

    const result = await client.specCheck(request);

    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('https://api.example.test/api/v1/governance/spec-check');
    expect(init.method).toBe('POST');
    expect(JSON.parse(init.body as string)).toEqual(request);
    expect(result).toEqual(body);
    expectTypeOf(result).toEqualTypeOf<GovernanceReport>();
  });

  it('computeConfidence POSTs to /api/v1/confidence', async () => {
    const body: ConfidenceResponse = { confidence: 0.5, rationale: 'jaccard=0.5' };
    const { client, fetchImpl } = makeClient(() => jsonResponse(body));
    const request: ConfidenceRequest = {
      requirement_text: 'must verify',
      artifact_text: 'verifies that',
    };

    const result = await client.computeConfidence(request);

    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('https://api.example.test/api/v1/confidence');
    expect(init.method).toBe('POST');
    expect(JSON.parse(init.body as string)).toEqual(request);
    expect(result).toEqual(body);
    expectTypeOf(result).toEqualTypeOf<ConfidenceResponse>();
  });

  it('listEvidence GETs /api/v1/evidence', async () => {
    const body: EvidenceResponse[] = [
      {
        id: 'ev-1',
        artifact_id: 'c-1',
        kind: 'test_run',
        url: 'https://ci.example.test/runs/1',
        captured_at: '2026-06-16T00:00:00Z',
        description: null,
        metadata: {},
        created_at: '2026-06-16T00:00:00Z',
        updated_at: '2026-06-16T00:00:00Z',
      },
    ];
    const { client, fetchImpl } = makeClient(() => jsonResponse(body));

    const result = await client.listEvidence();

    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('https://api.example.test/api/v1/evidence');
    expect(init.method).toBe('GET');
    expect(result).toEqual(body);
    expectTypeOf(result).toEqualTypeOf<EvidenceResponse[]>();
  });

  it('createEvidence POSTs to /api/v1/evidence', async () => {
    const body: EvidenceResponse = {
      id: 'ev-2',
      artifact_id: 'c-1',
      kind: 'screenshot',
      url: 'https://files.example.test/x.png',
      captured_at: '2026-06-16T00:00:00Z',
      description: 'shot',
      metadata: { sha: 'abc' },
      created_at: '2026-06-16T00:00:00Z',
      updated_at: '2026-06-16T00:00:00Z',
    };
    const { client, fetchImpl } = makeClient(() => jsonResponse(body));
    const payload: EvidenceCreate = {
      artifact_id: 'c-1',
      kind: 'screenshot',
      url: 'https://files.example.test/x.png',
      captured_at: '2026-06-16T00:00:00Z',
      description: 'shot',
      metadata: { sha: 'abc' },
    };

    const result = await client.createEvidence(payload);

    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('https://api.example.test/api/v1/evidence');
    expect(init.method).toBe('POST');
    expect(JSON.parse(init.body as string)).toEqual(payload);
    expect(result).toEqual(body);
    expectTypeOf(result).toEqualTypeOf<EvidenceResponse>();
  });

  it('throws on non-2xx responses', async () => {
    const { client } = makeClient(() => jsonResponse({}, { status: 500 }));
    await expect(client.buildCoverageMatrix({ links: [] })).rejects.toThrow(
      /coverage-matrix failed \(500\)/,
    );
  });
});
