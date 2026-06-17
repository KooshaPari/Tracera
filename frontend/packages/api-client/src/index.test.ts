import { describe, expect, expectTypeOf, it, vi } from 'vitest';
import { fetchCoverageMatrix } from './index.js';
import type { CoverageMatrixRequest, CoverageMatrixResponse } from '@tracertm/types';

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
