/**
 * Tests for diff export utilities
 */

import type { VersionDiff } from '@repo/types';

import { describe, expect, it } from 'vitest';

import { exportDiff } from '@/lib/diff-export';

const mockDiff: VersionDiff = {
  added: [
    {
      changeType: 'added',
      itemId: 'item3',
      significance: 'major',
      title: 'New Feature',
      type: 'feature',
    },
  ],
  computedAt: new Date().toISOString(),
  modified: [
    {
      changeType: 'modified',
      fieldChanges: [
        {
          changeType: 'modified',
          field: 'status',
          newValue: 'closed',
          oldValue: 'open',
        },
        {
          changeType: 'modified',
          field: 'priority',
          newValue: 'high',
          oldValue: 'low',
        },
      ],
      itemId: 'item1',
      significance: 'moderate',
      title: 'Modified Requirement',
      type: 'requirement',
    },
  ],
  removed: [
    {
      changeType: 'removed',
      itemId: 'item2',
      significance: 'minor',
      title: 'Old Bug',
      type: 'bug',
    },
  ],
  stats: {
    addedCount: 1,
    modifiedCount: 1,
    removedCount: 1,
    totalChanges: 3,
    unchangedCount: 5,
  },
  unchanged: 5,
  versionA: 'v1',
  versionANumber: 1,
  versionB: 'v2',
  versionBNumber: 2,
};

describe(exportDiff, () => {
  describe('JSON export', () => {
    it('should export diff as JSON', async () => {
      const result = await exportDiff(mockDiff, {
        format: 'json',
        includeFieldChanges: true,
        includeUnchanged: false,
      });

      expect(result.mimeType).toBe('application/json');
      expect(result.filename).toMatch(/\.json$/);

      const data = JSON.parse(result.content as string);
      expect(data.metadata.versionA).toBe('v1');
      expect(data.metadata.versionB).toBe('v2');
      expect(data.statistics.totalChanges).toBe(3);
      expect(data.added).toHaveLength(1);
      expect(data.removed).toHaveLength(1);
      expect(data.modified).toHaveLength(1);
    });

    it('should include field changes in JSON export when requested', async () => {
      const result = await exportDiff(mockDiff, {
        format: 'json',
        includeFieldChanges: true,
        includeUnchanged: false,
      });

      const data = JSON.parse(result.content as string);
      const modifiedItem = data.modified[0];
      expect(modifiedItem.fieldChanges).toHaveLength(2);
      expect(modifiedItem.fieldChanges[0].field).toBe('status');
    });
  });

  describe('CSV export', () => {
    it('should export diff as CSV', async () => {
      const result = await exportDiff(mockDiff, {
        format: 'csv',
        includeFieldChanges: false,
        includeUnchanged: false,
      });

      expect(result.mimeType).toBe('text/csv');
      expect(result.filename).toMatch(/\.csv$/);
      expect(result.content).toContain('Item ID,Title,Type');
      expect(result.content).toContain('New Feature');
      expect(result.content).toContain('Old Bug');
    });

    it('should handle CSV field escaping', async () => {
      const diffWithCommas: VersionDiff = {
        ...mockDiff,
        added: [
          {
            changeType: 'added',
            itemId: 'item1',
            significance: 'major',
            title: 'Feature with "quotes" and, commas',
            type: 'feature',
          },
        ],
      };

      const result = await exportDiff(diffWithCommas, {
        format: 'csv',
        includeFieldChanges: false,
        includeUnchanged: false,
      });

      const content = result.content as string;
      expect(content).toContain('Feature with "quotes" and, commas');
    });
  });

  describe('Markdown export', () => {
    it('should export diff as Markdown', async () => {
      const result = await exportDiff(mockDiff, {
        format: 'markdown',
        includeFieldChanges: true,
        includeUnchanged: false,
      });

      expect(result.mimeType).toBe('text/markdown');
      expect(result.filename).toMatch(/\.md$/);
      expect(result.content).toContain('# Version Diff Report');
      expect(result.content).toContain('## Added Items');
      expect(result.content).toContain('## Removed Items');
      expect(result.content).toContain('## Modified Items');
    });

    it('should include statistics in Markdown', async () => {
      const result = await exportDiff(mockDiff, {
        format: 'markdown',
        includeFieldChanges: false,
        includeUnchanged: false,
      });

      const content = result.content as string;
      expect(content).toContain('## Statistics');
      expect(content).toContain('| Added | 1 |');
      expect(content).toContain('| Removed | 1 |');
      expect(content).toContain('| Modified | 1 |');
    });

    it('should include field changes in Markdown when requested', async () => {
      const result = await exportDiff(mockDiff, {
        format: 'markdown',
        includeFieldChanges: true,
        includeUnchanged: false,
      });

      const content = result.content as string;
      expect(content).toContain('#### Field Changes');
      expect(content).toContain('status');
      expect(content).toContain('priority');
    });
  });

  describe('HTML export', () => {
    it('should export diff as HTML', async () => {
      const result = await exportDiff(mockDiff, {
        format: 'html',
        includeFieldChanges: true,
        includeUnchanged: false,
      });

      expect(result.mimeType).toBe('text/html');
      expect(result.filename).toMatch(/\.html$/);
      expect(result.content).toContain('<!DOCTYPE html>');
      expect(result.content).toContain('Version Diff Report');
    });

    it('should include statistics in HTML', async () => {
      const result = await exportDiff(mockDiff, {
        format: 'html',
        includeFieldChanges: false,
        includeUnchanged: false,
      });

      const content = result.content as string;
      expect(content).toContain('1');
      expect(content).toContain('Added');
      expect(content).toContain('Removed');
    });

    it('should format tables properly in HTML', async () => {
      const result = await exportDiff(mockDiff, {
        format: 'html',
        includeFieldChanges: false,
        includeUnchanged: false,
      });

      const content = result.content as string;
      expect(content).toContain('<table>');
      expect(content).toContain('<thead>');
      expect(content).toContain('<tbody>');
    });
  });

  describe('Filename generation', () => {
    it('should generate correct filename with date', async () => {
      const result = await exportDiff(mockDiff, {
        format: 'json',
        includeFieldChanges: false,
        includeUnchanged: false,
      });

      expect(result.filename).toMatch(/diff-v1-v2-\d{4}-\d{2}-\d{2}\.json/);
    });
  });

  describe('Unsupported format', () => {
    it('should throw error for unsupported format', async () => {
      await expect(
        exportDiff(mockDiff, {
          format: 'xml' as any,
          includeFieldChanges: false,
          includeUnchanged: false,
        }),
      ).rejects.toThrow('Unsupported export format');
    });
  });

  describe('Empty diff handling', () => {
    it('should handle empty diff', async () => {
      const emptyDiff: VersionDiff = {
        ...mockDiff,
        added: [],
        removed: [],
        modified: [],
        unchanged: 10,
        stats: {
          addedCount: 0,
          modifiedCount: 0,
          removedCount: 0,
          totalChanges: 0,
          unchangedCount: 10,
        },
      };

      const result = await exportDiff(emptyDiff, {
        format: 'json',
        includeFieldChanges: false,
        includeUnchanged: false,
      });

      const data = JSON.parse(result.content as string);
      expect(data.statistics.totalChanges).toBe(0);
    });
  });

  describe('Large dataset handling', () => {
    it('should handle large diff efficiently', async () => {
      const largeItems = Array.from({ length: 1000 }, (_, i) => ({
        changeType: 'added' as const,
        itemId: `item${i}`,
        significance: 'minor' as const,
        title: `Feature ${i}`,
        type: 'feature',
      }));

      const largeDiff: VersionDiff = {
        ...mockDiff,
        added: largeItems,
        stats: {
          addedCount: 1000,
          modifiedCount: 0,
          removedCount: 0,
          totalChanges: 1000,
          unchangedCount: 0,
        },
      };

      const result = await exportDiff(largeDiff, {
        format: 'json',
        includeFieldChanges: false,
        includeUnchanged: false,
      });

      expect(result.content).toBeTruthy();
      const data = JSON.parse(result.content as string);
      expect(data.added).toHaveLength(1000);
    });
  });

  describe('Field change serialization', () => {
    it('should properly serialize complex values', async () => {
      const diffWithComplexValues: VersionDiff = {
        ...mockDiff,
        modified: [
          {
            changeType: 'modified',
            fieldChanges: [
              {
                changeType: 'modified',
                field: 'settings',
                newValue: { retries: 5, timeout: 10_000 },
                oldValue: { retries: 3, timeout: 5000 },
              },
              {
                changeType: 'modified',
                field: 'tags',
                newValue: ['v2', 'stable', 'beta'],
                oldValue: ['v1', 'stable'],
              },
            ],
            itemId: 'item1',
            significance: 'major',
            title: 'Configuration',
            type: 'config',
          },
        ],
      };

      const result = await exportDiff(diffWithComplexValues, {
        format: 'json',
        includeFieldChanges: true,
        includeUnchanged: false,
      });

      const data = JSON.parse(result.content as string);
      expect(data.modified[0].fieldChanges[0].oldValue.timeout).toBe(5000);
      expect(data.modified[0].fieldChanges[1].newValue).toContain('v2');
    });
  });
});
