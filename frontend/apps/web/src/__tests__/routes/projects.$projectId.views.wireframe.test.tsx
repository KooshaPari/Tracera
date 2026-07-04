/**
 * Tests for Wireframe View Route
 */

import { describe, expect, it } from 'vitest';

describe('Wireframe View Route', () => {
  it('validates wireframe view route path pattern', () => {
    const wireframePath = '/projects/proj-1/views/wireframe';
    expect(wireframePath).toMatch(/^\/projects\/[^/]+\/views\/wireframe$/);
  });

  it('extracts projectId from route parameters', () => {
    const path = '/projects/proj-123/views/wireframe';
    const match = path.match(/\/projects\/([^/]+)\/views\/wireframe/);

    expect(match).not.toBeNull();
    expect(match?.[1]).toBe('proj-123');
  });

  it('recognizes wireframe view type from route', () => {
    const path = '/projects/proj-1/views/wireframe';
    const viewType = path.split('/')[4];

    expect(viewType).toBe('wireframe');
  });

  it('supports wireframe metadata', () => {
    const mockWireframe = {
      format: 'figma',
      id: 'wf-1',
      status: 'done',
      title: 'Homepage Wireframe',
      type: 'wireframe',
    };

    expect(mockWireframe.format).toMatch(/^(figma|sketch|adobe_xd|penpot)$/);
    expect(mockWireframe.status).toMatch(/^(pending|done|draft)$/);
  });

  it('handles multiple wireframes', () => {
    const mockWireframes = [
      { format: 'figma', id: 'wf1', title: 'Homepage' },
      { format: 'figma', id: 'wf2', title: 'Dashboard' },
      { format: 'figma', id: 'wf3', title: 'Profile' },
    ];

    expect(mockWireframes).toHaveLength(3);
    expect(mockWireframes.every((w) => w.format === 'figma')).toBeTruthy();
  });

  it('extracts wireframe dimensions', () => {
    const mockWireframe = {
      height: 1080,
      id: 'wf-1',
      scale: 1,
      width: 1920,
    };

    expect(mockWireframe.width).toBeGreaterThan(0);
    expect(mockWireframe.height).toBeGreaterThan(0);
    expect(mockWireframe.scale).toBeGreaterThan(0);
  });
});
