// Tests for LOD (level-of-detail) utilities — graph node zoom/count-based LOD
// @see docs/guides/SKELETON_AND_LOD_DESIGN.md

import { describe, expect, it } from 'vitest';

import {
  LODLevel,
  LOD_NODE_COUNT_THRESHOLD,
  determineLODLevel,
  getLODZoomThreshold,
  shouldUseSimplifiedNode,
} from '../../../../components/graph/utils/lod';

describe('LOD utilities', () => {
  describe(determineLODLevel, () => {
    it('returns VeryFar when zoom < 0.2', () => {
      expect(determineLODLevel(0)).toBe(LODLevel.VeryFar);
      expect(determineLODLevel(0.1)).toBe(LODLevel.VeryFar);
      expect(determineLODLevel(0.19)).toBe(LODLevel.VeryFar);
    });

    it('returns Far when 0.2 <= zoom < 0.5', () => {
      expect(determineLODLevel(0.2)).toBe(LODLevel.Far);
      expect(determineLODLevel(0.3)).toBe(LODLevel.Far);
      expect(determineLODLevel(0.49)).toBe(LODLevel.Far);
    });

    it('returns Medium when 0.5 <= zoom < 1.0', () => {
      expect(determineLODLevel(0.5)).toBe(LODLevel.Medium);
      expect(determineLODLevel(0.75)).toBe(LODLevel.Medium);
      expect(determineLODLevel(0.99)).toBe(LODLevel.Medium);
    });

    it('returns Close when 1.0 <= zoom < 2.0', () => {
      expect(determineLODLevel(1)).toBe(LODLevel.Close);
      expect(determineLODLevel(1.5)).toBe(LODLevel.Close);
      expect(determineLODLevel(1.99)).toBe(LODLevel.Close);
    });

    it('returns VeryClose when zoom >= 2.0', () => {
      expect(determineLODLevel(2)).toBe(LODLevel.VeryClose);
      expect(determineLODLevel(3)).toBe(LODLevel.VeryClose);
    });

    it('caps at Medium when nodeCount >= threshold and zoom would give Close/VeryClose', () => {
      const _threshold = LOD_NODE_COUNT_THRESHOLD; // 100
      expect(determineLODLevel(1, { nodeCount: 100 })).toBe(LODLevel.Medium);
      expect(determineLODLevel(1.5, { nodeCount: 150 })).toBe(LODLevel.Medium);
      expect(determineLODLevel(2, { nodeCount: 200 })).toBe(LODLevel.Medium);
    });

    it('does not cap when nodeCount is below threshold', () => {
      expect(determineLODLevel(1, { nodeCount: 99 })).toBe(LODLevel.Close);
      expect(determineLODLevel(2, { nodeCount: 50 })).toBe(LODLevel.VeryClose);
    });

    it('does not cap when nodeCount is at threshold but zoom already gives Medium or lower', () => {
      expect(determineLODLevel(0.5, { nodeCount: 100 })).toBe(LODLevel.Medium);
      expect(determineLODLevel(0.2, { nodeCount: 100 })).toBe(LODLevel.Far);
    });

    it('respects custom forceSimplifiedAbove option', () => {
      expect(determineLODLevel(1.5, { forceSimplifiedAbove: 40, nodeCount: 50 })).toBe(
        LODLevel.Medium,
      );
      expect(determineLODLevel(1.5, { forceSimplifiedAbove: 40, nodeCount: 30 })).toBe(
        LODLevel.Close,
      );
    });
  });

  describe(shouldUseSimplifiedNode, () => {
    it('returns true for VeryFar, Far, Medium', () => {
      expect(shouldUseSimplifiedNode(LODLevel.VeryFar)).toBeTruthy();
      expect(shouldUseSimplifiedNode(LODLevel.Far)).toBeTruthy();
      expect(shouldUseSimplifiedNode(LODLevel.Medium)).toBeTruthy();
    });

    it('returns false for Close and VeryClose', () => {
      expect(shouldUseSimplifiedNode(LODLevel.Close)).toBeFalsy();
      expect(shouldUseSimplifiedNode(LODLevel.VeryClose)).toBeFalsy();
    });
  });

  describe(getLODZoomThreshold, () => {
    it('returns correct lower-bound zoom for each level', () => {
      expect(getLODZoomThreshold(LODLevel.VeryFar)).toBe(0);
      expect(getLODZoomThreshold(LODLevel.Far)).toBe(0.2);
      expect(getLODZoomThreshold(LODLevel.Medium)).toBe(0.5);
      expect(getLODZoomThreshold(LODLevel.Close)).toBe(1);
      expect(getLODZoomThreshold(LODLevel.VeryClose)).toBe(2);
    });
  });

  describe(LOD_NODE_COUNT_THRESHOLD, () => {
    it('is 100 by default', () => {
      expect(LOD_NODE_COUNT_THRESHOLD).toBe(100);
    });
  });
});
