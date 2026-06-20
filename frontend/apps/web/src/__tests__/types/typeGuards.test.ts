import { describe, expect, it } from 'vitest';

import type { Item } from '@tracertm/types';

import {
  hasSpec,
  isDefectItem,
  isEpicItem,
  isRequirementItem,
  isTaskItem,
  isTestItem,
  isUserStoryItem,
} from '@tracertm/types';

function createMockItem(type: string): Item {
  return {
    createdAt: '2026-01-30T00:00:00Z',
    id: 'test-id',
    priority: 'medium',
    projectId: 'project-1',
    status: 'todo',
    title: 'Test Item',
    type,
    updatedAt: '2026-01-30T00:00:00Z',
    version: 1,
    view: 'FEATURE',
  };
}

describe('Type Guards', () => {
  describe(isRequirementItem, () => {
    it('should return true for requirement type', () => {
      const item = createMockItem('requirement');
      expect(isRequirementItem(item)).toBeTruthy();
    });

    it('should return false for non-requirement types', () => {
      expect(isRequirementItem(createMockItem('test'))).toBeFalsy();
      expect(isRequirementItem(createMockItem('epic'))).toBeFalsy();
      expect(isRequirementItem(createMockItem('task'))).toBeFalsy();
    });

    it('should enable type-specific property access', () => {
      const item = createMockItem('requirement');
      if (isRequirementItem(item)) {
        // TypeScript should allow accessing RequirementItem-specific properties
        const { adrId } = item; // Should compile
        const { contractId } = item; // Should compile
        expect(adrId).toBeUndefined(); // These are optional
        expect(contractId).toBeUndefined();
      }
    });
  });

  describe(isTestItem, () => {
    it('should return true for test types', () => {
      expect(isTestItem(createMockItem('test'))).toBeTruthy();
      expect(isTestItem(createMockItem('test_case'))).toBeTruthy();
      expect(isTestItem(createMockItem('test_suite'))).toBeTruthy();
    });

    it('should return false for non-test types', () => {
      expect(isTestItem(createMockItem('requirement'))).toBeFalsy();
      expect(isTestItem(createMockItem('epic'))).toBeFalsy();
      expect(isTestItem(createMockItem('bug'))).toBeFalsy();
    });

    it('should enable type-specific property access', () => {
      const item = createMockItem('test');
      if (isTestItem(item)) {
        const { testType } = item; // Should compile
        const { automationStatus } = item; // Should compile
        expect(testType).toBeUndefined(); // Optional properties
        expect(automationStatus).toBeUndefined();
      }
    });
  });

  describe(isEpicItem, () => {
    it('should return true for epic type', () => {
      expect(isEpicItem(createMockItem('epic'))).toBeTruthy();
    });

    it('should return false for non-epic types', () => {
      expect(isEpicItem(createMockItem('requirement'))).toBeFalsy();
      expect(isEpicItem(createMockItem('user_story'))).toBeFalsy();
      expect(isEpicItem(createMockItem('task'))).toBeFalsy();
    });

    it('should enable type-specific property access', () => {
      const item = createMockItem('epic');
      if (isEpicItem(item)) {
        const { acceptanceCriteria } = item; // Should compile
        const { businessValue } = item; // Should compile
        expect(acceptanceCriteria).toBeUndefined();
        expect(businessValue).toBeUndefined();
      }
    });
  });

  describe(isUserStoryItem, () => {
    it('should return true for user story types', () => {
      expect(isUserStoryItem(createMockItem('user_story'))).toBeTruthy();
      expect(isUserStoryItem(createMockItem('story'))).toBeTruthy();
    });

    it('should return false for non-story types', () => {
      expect(isUserStoryItem(createMockItem('epic'))).toBeFalsy();
      expect(isUserStoryItem(createMockItem('requirement'))).toBeFalsy();
    });

    it('should enable type-specific property access', () => {
      const item = createMockItem('user_story');
      if (isUserStoryItem(item)) {
        const { asA } = item; // Should compile
        const { iWant } = item; // Should compile
        const { soThat } = item; // Should compile
        const { storyPoints } = item; // Should compile
        expect(asA).toBeUndefined();
        expect(iWant).toBeUndefined();
        expect(soThat).toBeUndefined();
        expect(storyPoints).toBeUndefined();
      }
    });
  });

  describe(isTaskItem, () => {
    it('should return true for task type', () => {
      expect(isTaskItem(createMockItem('task'))).toBeTruthy();
    });

    it('should return false for non-task types', () => {
      expect(isTaskItem(createMockItem('bug'))).toBeFalsy();
      expect(isTaskItem(createMockItem('user_story'))).toBeFalsy();
    });

    it('should enable type-specific property access', () => {
      const item = createMockItem('task');
      if (isTaskItem(item)) {
        const { estimatedHours } = item; // Should compile
        const { actualHours } = item; // Should compile
        expect(estimatedHours).toBeUndefined();
        expect(actualHours).toBeUndefined();
      }
    });
  });

  describe(isDefectItem, () => {
    it('should return true for defect types', () => {
      expect(isDefectItem(createMockItem('bug'))).toBeTruthy();
      expect(isDefectItem(createMockItem('defect'))).toBeTruthy();
    });

    it('should return false for non-defect types', () => {
      expect(isDefectItem(createMockItem('task'))).toBeFalsy();
      expect(isDefectItem(createMockItem('test'))).toBeFalsy();
    });

    it('should enable type-specific property access', () => {
      const item = createMockItem('bug');
      if (isDefectItem(item)) {
        const { severity } = item; // Should compile
        const { reproducible } = item; // Should compile
        const { stepsToReproduce } = item; // Should compile
        expect(severity).toBeUndefined();
        expect(reproducible).toBeUndefined();
        expect(stepsToReproduce).toBeUndefined();
      }
    });
  });

  describe(hasSpec, () => {
    it('should return true for requirement items', () => {
      expect(hasSpec(createMockItem('requirement'))).toBeTruthy();
    });

    it('should return false for non-specification items', () => {
      expect(hasSpec(createMockItem('test'))).toBeFalsy();
      expect(hasSpec(createMockItem('epic'))).toBeFalsy();
      expect(hasSpec(createMockItem('bug'))).toBeFalsy();
    });

    it('should be equivalent to isRequirementItem', () => {
      const requirementItem = createMockItem('requirement');
      const testItem = createMockItem('test');

      expect(hasSpec(requirementItem)).toBe(isRequirementItem(requirementItem));
      expect(hasSpec(testItem)).toBe(isRequirementItem(testItem));
    });
  });

  describe('Type narrowing in switch statements', () => {
    it('should work with discriminated union', () => {
      const item = createMockItem('requirement');

      switch (item.type) {
        case 'requirement': {
          // TypeScript should narrow to RequirementItem
          expect(item.type).toBe('requirement');
          break;
        }
        case 'test':
        case 'test_case':
        case 'test_suite': {
          // TypeScript should narrow to TestItem
          expect(item.type).toMatch(/^test/);
          break;
        }
        default: {
          // Other types
          break;
        }
      }
    });
  });

  describe('Type guard composition', () => {
    it('should work with multiple type guards', () => {
      const items = [
        createMockItem('requirement'),
        createMockItem('test'),
        createMockItem('epic'),
        createMockItem('bug'),
      ];

      const requirements = items.filter(isRequirementItem);
      const tests = items.filter(isTestItem);
      const defects = items.filter(isDefectItem);

      expect(requirements).toHaveLength(1);
      expect(tests).toHaveLength(1);
      expect(defects).toHaveLength(1);
    });
  });
});
