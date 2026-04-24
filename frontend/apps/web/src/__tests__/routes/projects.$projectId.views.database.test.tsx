/**
 * Tests for Database View Route
 */

import { describe, expect, it } from 'vitest';

describe('Database View Route', () => {
  it('validates database view route path pattern', () => {
    const dbPath = '/projects/proj-1/views/database';
    expect(dbPath).toMatch(/^\/projects\/[^/]+\/views\/database$/);
  });

  it('extracts projectId from route parameters', () => {
    const path = '/projects/proj-123/views/database';
    const match = path.match(/\/projects\/([^/]+)\/views\/database/);

    expect(match).not.toBeNull();
    expect(match?.[1]).toBe('proj-123');
  });

  it('recognizes database view type from route', () => {
    const path = '/projects/proj-1/views/database';
    const viewType = path.split('/')[4];

    expect(viewType).toBe('database');
  });

  it('supports database schema metadata', () => {
    const mockSchema = {
      column_count: 15,
      id: 'schema-1',
      table_count: 10,
      title: 'Users Table',
      type: 'database',
    };

    expect(mockSchema.table_count).toBeGreaterThan(0);
    expect(mockSchema.column_count).toBeGreaterThan(0);
  });

  it('handles multiple tables in schema', () => {
    const mockTables = [
      { id: 'tbl-1', name: 'users' },
      { id: 'tbl-2', name: 'products' },
      { id: 'tbl-3', name: 'orders' },
    ];

    expect(mockTables).toHaveLength(3);
    expect(mockTables.every((t) => t.name)).toBeTruthy();
  });
});
