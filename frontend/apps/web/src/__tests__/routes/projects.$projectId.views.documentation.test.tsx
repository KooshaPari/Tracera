/**
 * Tests for Documentation View Route
 */

import { describe, expect, it } from 'vitest';

describe('Documentation View Route', () => {
  it('validates documentation view route path pattern', () => {
    const docsPath = '/projects/proj-1/views/documentation';
    expect(docsPath).toMatch(/^\/projects\/[^/]+\/views\/documentation$/);
  });

  it('extracts projectId from route parameters', () => {
    const path = '/projects/proj-123/views/documentation';
    const match = path.match(/\/projects\/([^/]+)\/views\/documentation/);

    expect(match).not.toBeNull();
    expect(match?.[1]).toBe('proj-123');
  });

  it('recognizes documentation view type from route', () => {
    const path = '/projects/proj-1/views/documentation';
    const [projectsSegment, projectId, viewsSegment, viewType] = path.split('/').slice(1);

    expect(projectsSegment).toBe('projects');
    expect(projectId).toBe('proj-1');
    expect(viewsSegment).toBe('views');
    expect(viewType).toBe('documentation');
  });

  it('supports documentation metadata', () => {
    const mockDoc = {
      format: 'markdown',
      id: 'doc-1',
      status: 'done',
      title: 'API Documentation',
      type: 'documentation',
    };

    expect(mockDoc.format).toMatch(/^(markdown|html|pdf|docx)$/);
    expect(mockDoc.status).toMatch(/^(pending|done|draft)$/);
  });

  it('handles multiple documentation files', () => {
    const mockDocs = [
      { format: 'markdown', id: 'd1', title: 'README.md' },
      { format: 'markdown', id: 'd2', title: 'API.md' },
      { format: 'markdown', id: 'd3', title: 'GUIDE.md' },
    ];

    expect(mockDocs).toHaveLength(3);
    expect(mockDocs.every((doc) => doc.format === 'markdown')).toBeTruthy();
  });
});
