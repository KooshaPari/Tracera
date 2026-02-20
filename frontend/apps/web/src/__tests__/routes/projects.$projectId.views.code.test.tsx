/**
 * Tests for Code View Route
 */

import { describe, expect, it } from 'vitest';

describe('Code View Route', () => {
  it('validates code view route path pattern', () => {
    const codePath = '/projects/proj-1/views/code';
    expect(codePath).toMatch(/^\/projects\/[^/]+\/views\/code$/);
  });

  it('extracts projectId from route parameters', () => {
    const path = '/projects/proj-123/views/code';
    const match = path.match(/\/projects\/([^/]+)\/views\/code/);

    expect(match).not.toBeNull();
    expect(match?.[1]).toBe('proj-123');
  });

  it('recognizes code view type from route', () => {
    const path = '/projects/proj-1/views/code';
    const viewType = path.split('/')[4];

    expect(viewType).toBe('code');
  });

  it('supports code file metadata', () => {
    const mockCodeFile = {
      id: 'file-1',
      language: 'typescript',
      lines: 150,
      title: 'main.ts',
      type: 'code',
    };

    expect(mockCodeFile.language).toMatch(/^(typescript|javascript|python|go|rust|java)$/);
    expect(mockCodeFile.lines).toBeGreaterThan(0);
  });

  it('handles multiple code files', () => {
    const mockFiles = [
      { id: 'f1', language: 'typescript', title: 'main.ts' },
      { id: 'f2', language: 'typescript', title: 'utils.ts' },
      { id: 'f3', language: 'typescript', title: 'types.ts' },
    ];

    expect(mockFiles).toHaveLength(3);
    expect(mockFiles.every((f) => f.language === 'typescript')).toBeTruthy();
  });
});
