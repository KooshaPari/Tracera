/**
 * Smoke tests for Rich Node Interaction components
 * These tests verify that components export correctly and can be imported
 */

import { describe, expect, it } from 'vitest';

// Import components directly
import { NodeActions } from '../../../components/graph/NodeActions';
import { NodeContextMenu } from '../../../components/graph/NodeContextMenu';
import { NodeHoverTooltip } from '../../../components/graph/NodeHoverTooltip';
import { NodeQuickActions } from '../../../components/graph/NodeQuickActions';

describe('Rich Node Interactions - Component Exports', () => {
  it('exports NodeActions component', () => {
    expect(NodeActions).toBeDefined();
    expect(typeof NodeActions).toBe('object');
    // Memoized components are objects, not functions
    expect(NodeActions.$$typeof).toBeDefined();
  });

  it('exports NodeContextMenu component', () => {
    expect(NodeContextMenu).toBeDefined();
    expect(typeof NodeContextMenu).toBe('object');
    // Memoized components are objects, not functions
    expect(NodeContextMenu.$$typeof).toBeDefined();
  });

  it('exports NodeHoverTooltip component', () => {
    expect(NodeHoverTooltip).toBeDefined();
    expect(typeof NodeHoverTooltip).toBe('object');
    // Memoized components are objects, not functions
    expect(NodeHoverTooltip.$$typeof).toBeDefined();
  });

  it('exports NodeQuickActions component', () => {
    expect(NodeQuickActions).toBeDefined();
    expect(typeof NodeQuickActions).toBe('object');
    // Memoized components are objects, not functions
    expect(NodeQuickActions.$$typeof).toBeDefined();
  });
});
