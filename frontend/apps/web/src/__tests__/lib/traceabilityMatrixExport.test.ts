import { describe, expect, it } from 'vitest';

import { buildTraceabilityMatrixCsv, getCoverageStatus } from '../../lib/traceabilityMatrixExport';

describe('traceabilityMatrixExport', () => {
  it('classifies coverage status', () => {
    expect(getCoverageStatus(0, 3)).toBe('uncovered');
    expect(getCoverageStatus(1, 3)).toBe('partial');
    expect(getCoverageStatus(3, 3)).toBe('covered');
  });

  it('builds CSV with headers and link cells', () => {
    const requirements = [{ id: 'req-1', title: 'Login' }];
    const features = [
      { id: 'feat-1', title: 'Auth API' },
      { id: 'feat-2', title: 'Session' },
    ];
    const coverage = { 'req-1': new Set(['feat-1']) };

    const csv = buildTraceabilityMatrixCsv(requirements, features, coverage);

    expect(csv).toContain('"Requirement ID"');
    expect(csv).toContain('"Login"');
    expect(csv).toContain('"PARTIAL"');
    expect(csv).toContain('"linked"');
    expect(csv.split('\n').length).toBeGreaterThan(2);
  });
});
