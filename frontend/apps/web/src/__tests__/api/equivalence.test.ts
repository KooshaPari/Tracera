import * as Vitest from 'vitest';

import * as EquivalenceApi from '../../api/equivalence';

type ConfirmEquivalenceInput = EquivalenceApi.ConfirmEquivalenceInput;
type DetectEquivalencesInput = EquivalenceApi.DetectEquivalencesInput;
type EquivalenceLink = EquivalenceApi.EquivalenceLink;
type RejectEquivalenceInput = EquivalenceApi.RejectEquivalenceInput;
const { equivalenceQueryKeys } = EquivalenceApi;

Vitest.describe('equivalence API hooks', () => {
  Vitest.describe('queryKeys', () => {
    Vitest.it('should generate correct query key for all equivalences', () => {
      const key = equivalenceQueryKeys.all;
      Vitest.expect(key).toEqual(['equivalences']);
    });

    Vitest.it('should generate correct query key for list with projectId and status', () => {
      const key = equivalenceQueryKeys.list('project-1', 'pending');
      Vitest.expect(key).toEqual(['equivalences', 'list', 'project-1', 'pending']);
    });

    Vitest.it('should generate correct query key for list with projectId only', () => {
      const key = equivalenceQueryKeys.list('project-1');
      Vitest.expect(key).toEqual(['equivalences', 'list', 'project-1', undefined]);
    });

    Vitest.it('should generate correct query key for detail', () => {
      const key = equivalenceQueryKeys.detail('equiv-1');
      Vitest.expect(key).toEqual(['equivalences', 'detail', 'equiv-1']);
    });
  });

  Vitest.describe('EquivalenceLink type', () => {
    Vitest.it('should validate equivalence link structure', () => {
      const link: EquivalenceLink = {
        confidence: 0.88,
        createdAt: '2024-01-01T00:00:00Z',
        id: 'equiv-1',
        itemId1: 'item-1',
        itemId2: 'item-2',
        similarity: 0.95,
        status: 'pending',
      };

      Vitest.expect(link.id).toBeDefined();
      Vitest.expect(link.itemId1).toBeDefined();
      Vitest.expect(link.itemId2).toBeDefined();
      Vitest.expect(link.similarity).toBeGreaterThan(0);
      Vitest.expect(link.confidence).toBeGreaterThan(0);
      Vitest.expect(['pending', 'confirmed', 'rejected']).toContain(link.status);
    });

    Vitest.it('should allow optional confirmedAt field', () => {
      const link: EquivalenceLink = {
        confidence: 0.88,
        confirmedAt: '2024-01-02T00:00:00Z',
        createdAt: '2024-01-01T00:00:00Z',
        id: 'equiv-1',
        itemId1: 'item-1',
        itemId2: 'item-2',
        similarity: 0.95,
        status: 'confirmed',
      };

      Vitest.expect(link.confirmedAt).toBeDefined();
    });
  });

  Vitest.describe('Input types', () => {
    Vitest.it('should validate DetectEquivalencesInput', () => {
      const input: DetectEquivalencesInput = {
        projectId: 'project-1',
        threshold: 0.8,
      };

      Vitest.expect(input.projectId).toBeDefined();
      Vitest.expect(input.threshold).toBeDefined();
    });

    Vitest.it('should validate ConfirmEquivalenceInput', () => {
      const input: ConfirmEquivalenceInput = {
        comment: 'Confirmed as equivalent',
        equivalenceId: 'equiv-1',
      };

      Vitest.expect(input.equivalenceId).toBeDefined();
    });

    Vitest.it('should validate RejectEquivalenceInput', () => {
      const input: RejectEquivalenceInput = {
        equivalenceId: 'equiv-1',
        reason: 'False positive',
      };

      Vitest.expect(input.equivalenceId).toBeDefined();
    });
  });

  Vitest.describe('Query key hierarchies', () => {
    Vitest.it('should create consistent list query keys', () => {
      const key1 = equivalenceQueryKeys.list('project-1');
      const key2 = equivalenceQueryKeys.list('project-2');

      Vitest.expect(key1).not.toEqual(key2);
      Vitest.expect(key1[0]).toEqual(key2[0]); // Same root
    });

    Vitest.it('should invalidate all lists when using lists key', () => {
      const listsKey = equivalenceQueryKeys.lists();
      const specificKey = equivalenceQueryKeys.list('project-1');

      Vitest.expect(listsKey).toEqual(['equivalences', 'list']);
      Vitest.expect(specificKey.slice(0, 2)).toEqual(listsKey);
    });
  });
});
