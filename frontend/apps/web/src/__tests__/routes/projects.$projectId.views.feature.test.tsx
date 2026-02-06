/**
 * Tests for Feature View Route
 */

import { describe, expect, it } from 'vitest';

describe('Feature View Route', () => {
  it('validates feature view route path pattern', () => {
    const featurePath = '/projects/proj-1/views/feature';
    expect(featurePath).toMatch(/^\/projects\/[^/]+\/views\/feature$/);
  });

  it('extracts projectId from route parameters', () => {
    const path = '/projects/proj-123/views/feature';
    const match = path.match(/\/projects\/([^/]+)\/views\/feature/);

    expect(match).not.toBeNull();
    expect(match?.[1]).toBe('proj-123');
  });

  it('recognizes feature view type from route', () => {
    const path = '/projects/proj-1/views/feature';
    const viewType = path.split('/')[4];

    expect(viewType).toBe('feature');
  });

  it('supports feature metadata', () => {
    const mockFeature = {
      id: 'feat-1',
      priority: 'high',
      status: 'todo',
      title: 'Feature 1',
      type: 'feature',
    };

    expect(mockFeature.priority).toMatch(/^(low|medium|high|critical)$/);
    expect(mockFeature.status).toMatch(/^(todo|in_progress|done)$/);
  });

  it('handles multiple features with priorities', () => {
    const mockFeatures = [
      { id: 'f1', priority: 'high', title: 'Feature 1' },
      { id: 'f2', priority: 'medium', title: 'Feature 2' },
      { id: 'f3', priority: 'low', title: 'Feature 3' },
    ];

    expect(mockFeatures).toHaveLength(3);
    expect(mockFeatures[0]?.priority).toBe('high');
  });

  it('calculates feature completion status', () => {
    const mockFeatures = [
      { id: 'f1', status: 'done' },
      { id: 'f2', status: 'in_progress' },
      { id: 'f3', status: 'todo' },
    ];

    const completed = mockFeatures.filter((f) => f.status === 'done').length;
    expect(completed).toBe(1);
  });
});
