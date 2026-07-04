import { describe, expect, it } from 'vitest';

import {
  getItemTypeColor,
  getItemTypeConfig,
  getItemTypeIcon,
  getItemTypeLabel,
  getItemTypesForView,
  ITEM_TYPE_CONFIGS,
  isTypeValidForView,
} from '@/lib/itemTypeConfig';

describe('itemTypeConfig', () => {
  describe('getItemTypeConfig', () => {
    it('should return config for known type', () => {
      const config = getItemTypeConfig('requirement');
      expect(config.type).toBe('requirement');
      expect(config.label).toBe('Requirement');
      expect(config.color).toBe('#9333ea');
      expect(config.requiresSpec).toBe(true);
    });

    it('should return generic config for unknown type', () => {
      const config = getItemTypeConfig('unknown_type');
      expect(config.type).toBe('generic');
      expect(config.label).toBe('Item');
    });
  });

  describe('getItemTypesForView', () => {
    it('should return types for FEATURE view', () => {
      const types = getItemTypesForView('FEATURE');
      const typeNames = types.map((t) => t.type);

      expect(typeNames).toContain('requirement');
      expect(typeNames).toContain('epic');
      expect(typeNames).toContain('user_story');
      expect(typeNames).toContain('feature');
      expect(typeNames).toContain('task');
    });

    it('should return types for TEST view', () => {
      const types = getItemTypesForView('TEST');
      const typeNames = types.map((t) => t.type);

      expect(typeNames).toContain('test');
      expect(typeNames).toContain('test_case');
      expect(typeNames).toContain('test_suite');
      expect(typeNames).toContain('bug');
    });

    it('should return types for CODE view', () => {
      const types = getItemTypesForView('CODE');
      const typeNames = types.map((t) => t.type);

      expect(typeNames).toContain('code');
      expect(typeNames).toContain('api');
      expect(typeNames).toContain('task');
    });
  });

  describe('isTypeValidForView', () => {
    it('should return true for valid type-view combinations', () => {
      expect(isTypeValidForView('requirement', 'FEATURE')).toBe(true);
      expect(isTypeValidForView('test', 'TEST')).toBe(true);
      expect(isTypeValidForView('api', 'API')).toBe(true);
    });

    it('should return false for invalid type-view combinations', () => {
      expect(isTypeValidForView('test', 'FEATURE')).toBe(false);
      expect(isTypeValidForView('wireframe', 'CODE')).toBe(false);
    });

    it('should return true for generic type (no allowed views restriction)', () => {
      // Generic type has no allowed views, so it's valid everywhere
      expect(isTypeValidForView('generic', 'FEATURE')).toBe(true);
      expect(isTypeValidForView('generic', 'TEST')).toBe(true);
    });
  });

  describe('helper functions', () => {
    it('should get correct icon', () => {
      expect(getItemTypeIcon('requirement')).toBe('requirement');
      expect(getItemTypeIcon('test')).toBe('test');
      expect(getItemTypeIcon('bug')).toBe('bug');
      expect(getItemTypeIcon('unknown')).toBe('generic');
    });

    it('should get correct color', () => {
      expect(getItemTypeColor('requirement')).toBe('#9333ea');
      expect(getItemTypeColor('test')).toBe('#22c55e');
      expect(getItemTypeColor('bug')).toBe('#ef4444');
      expect(getItemTypeColor('unknown')).toBe('#6b7280');
    });

    it('should get correct label', () => {
      expect(getItemTypeLabel('requirement')).toBe('Requirement');
      expect(getItemTypeLabel('test')).toBe('Test');
      expect(getItemTypeLabel('bug')).toBe('Bug');
      expect(getItemTypeLabel('unknown')).toBe('Item');
    });
  });

  describe('type configuration completeness', () => {
    it('should have configurations for all common types', () => {
      const requiredTypes = [
        'requirement',
        'epic',
        'user_story',
        'task',
        'bug',
        'test',
        'feature',
        'api',
        'database',
        'code',
        'wireframe',
      ];

      requiredTypes.forEach((type) => {
        expect(ITEM_TYPE_CONFIGS[type]).toBeDefined();
        expect(ITEM_TYPE_CONFIGS[type].label).toBeTruthy();
        expect(ITEM_TYPE_CONFIGS[type].color).toBeTruthy();
        expect(ITEM_TYPE_CONFIGS[type].icon).toBeTruthy();
      });
    });

    it('should have valid color codes', () => {
      const hexColorRegex = /^#[0-9a-f]{6}$/i;

      Object.values(ITEM_TYPE_CONFIGS).forEach((config) => {
        expect(config.color).toMatch(hexColorRegex);
      });
    });

    it('should have default priorities', () => {
      expect(ITEM_TYPE_CONFIGS.requirement.defaultPriority).toBe('high');
      expect(ITEM_TYPE_CONFIGS.bug.defaultPriority).toBe('high');
      expect(ITEM_TYPE_CONFIGS.security.defaultPriority).toBe('critical');
      expect(ITEM_TYPE_CONFIGS.task.defaultPriority).toBe('medium');
    });
  });
});
