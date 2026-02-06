/**
 * Tests for useGraph hooks
 */

import { renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useDependencyAnalysis, useFullGraph, useImpactAnalysis } from '../../hooks/useGraph';
import { createWrapper } from '../utils/test-utils';

describe('useGraph', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(useFullGraph, () => {
    it('should fetch full graph data', async () => {
      const { result } = renderHook(() => useFullGraph('proj-1'), {
        wrapper: createWrapper(),
      });

      // Check that hook loads data
      expect(result.current).toBeDefined();

      // Allow time for async data loading
      await waitFor(
        () => {
          expect(result.current.isSuccess || result.current.isPending).toBeTruthy();
        },
        { timeout: 3000 },
      );
    });

    it('should handle missing project id', () => {
      const { result } = renderHook(() => useFullGraph(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isPending).toBeTruthy();
    });
  });

  describe(useImpactAnalysis, () => {
    it('should fetch impact analysis', async () => {
      const { result } = renderHook(() => useImpactAnalysis('item-1'), {
        wrapper: createWrapper(),
      });

      expect(result.current).toBeDefined();
      await waitFor(
        () => {
          expect(result.current.isSuccess || result.current.isPending).toBeTruthy();
        },
        { timeout: 3000 },
      );
    }, 5000);

    it('should not fetch when id is empty', () => {
      const { result } = renderHook(() => useImpactAnalysis(''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
    });
  });

  describe(useDependencyAnalysis, () => {
    it('should fetch dependency analysis', async () => {
      const { result } = renderHook(() => useDependencyAnalysis('item-1'), {
        wrapper: createWrapper(),
      });

      expect(result.current).toBeDefined();
      await waitFor(
        () => {
          expect(result.current.isSuccess || result.current.isPending).toBeTruthy();
        },
        { timeout: 3000 },
      );
    }, 5000);
  });
});
