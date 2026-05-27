import { beforeEach, describe, expect, it, vi } from 'vitest';

import { fetchTraceMatrixCsv } from '@/api/traceMatrixExport';

describe('traceMatrixExport', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => 'test-token'),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    });
  });

  it('requests analysis trace-matrix export endpoint', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      text: async () => '"Source","Col"\n"Row","link"',
    } as Response);

    const csv = await fetchTraceMatrixCsv('proj-abc', {
      sourceView: 'requirements',
      targetView: 'feature',
    });

    expect(csv).toContain('Source');
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/analysis/trace-matrix/export?'),
      expect.objectContaining({ headers: expect.any(Object) }),
    );
    const url = vi.mocked(fetch).mock.calls[0]?.[0] as string;
    expect(url).toContain('project_id=proj-abc');
    expect(url).toContain('source_view=requirements');
    expect(url).toContain('target_view=feature');
  });

  it('throws when export fails', async () => {
    vi.mocked(fetch).mockResolvedValue({ ok: false, status: 503 } as Response);

    await expect(fetchTraceMatrixCsv('proj-1')).rejects.toThrow(/503/);
  });
});
