import { describe, it, expect } from 'vitest';

import type { SearchIndexConfig } from '../search-config';

import { searchConfig, formatSearchPreview } from '../search-config';

describe('searchConfig', () => {
  it('exports a valid SearchIndexConfig object', () => {
    expect(searchConfig).toBeDefined();
    expect(searchConfig.weights).toBeDefined();
    expect(searchConfig.priorityPages).toBeInstanceOf(Array);
    expect(typeof searchConfig.minQueryLength).toBe('number');
    expect(typeof searchConfig.maxResults).toBe('number');
  });

  it('has correct weight values with title having the highest weight', () => {
    const { weights } = searchConfig;
    expect(weights.title).toBe(10);
    expect(weights.description).toBe(5);
    expect(weights.heading).toBe(3);
    expect(weights.content).toBe(1);
    expect(weights.title).toBeGreaterThan(weights.description);
    expect(weights.description).toBeGreaterThan(weights.heading);
    expect(weights.heading).toBeGreaterThan(weights.content);
  });

  it('has expected priority pages', () => {
    expect(searchConfig.priorityPages).toContain('/docs');
    expect(searchConfig.priorityPages).toContain('/docs/getting-started');
    expect(searchConfig.priorityPages).toContain('/docs/getting-started/quick-start');
    expect(searchConfig.priorityPages).toContain('/docs/guides');
    expect(searchConfig.priorityPages).toHaveLength(4);
  });

  it('has minQueryLength of 2', () => {
    expect(searchConfig.minQueryLength).toBe(2);
  });

  it('has maxResults of 50', () => {
    expect(searchConfig.maxResults).toBe(50);
  });

  it('satisfies SearchIndexConfig type shape', () => {
    const config: SearchIndexConfig = searchConfig;
    expect(config).toBe(searchConfig);
  });
});

describe('formatSearchPreview', () => {
  it('returns truncated content when query is not found', () => {
    const content = 'This is a long piece of content that should be truncated';
    const result = formatSearchPreview(content, 'xyz', 20);
    expect(result).toBe('This is a long piece...');
  });

  it('returns content without ellipsis when shorter than maxLength and query not found', () => {
    const content = 'Short text';
    const result = formatSearchPreview(content, 'xyz', 150);
    expect(result).toBe('Short text');
  });

  it('highlights context around a match found at the beginning', () => {
    const content = 'React is a JavaScript library for building user interfaces';
    const result = formatSearchPreview(content, 'React', 150);
    expect(result).toContain('React');
    // Should not start with "..." because the match is at position 0
    expect(result.startsWith('...')).toBe(false);
  });

  it('highlights context around a match found in the middle of long text', () => {
    const prefix = 'A'.repeat(100);
    const content = `${prefix} target_word ${'B'.repeat(200)}`;
    const result = formatSearchPreview(content, 'target_word', 150);
    expect(result).toContain('target_word');
    // Should have leading "..." because the match is deep in the string
    expect(result.startsWith('...')).toBe(true);
    // Should have trailing "..." because there is content after the window
    expect(result.endsWith('...')).toBe(true);
  });

  it('is case-insensitive when searching for the match position', () => {
    const content = 'The Quick Brown Fox jumps over the lazy dog';
    const result = formatSearchPreview(content, 'QUICK', 150);
    expect(result).toContain('Quick');
  });

  it('uses default maxLength of 150 when not specified', () => {
    const content = 'A'.repeat(200);
    const result = formatSearchPreview(content, 'xyz');
    // Truncated to 150 + "..."
    expect(result).toBe('A'.repeat(150) + '...');
  });

  it('returns full content when content is shorter than maxLength and query not found', () => {
    const content = 'Hello world';
    const result = formatSearchPreview(content, 'notfound', 200);
    expect(result).toBe('Hello world');
  });

  it('handles empty content', () => {
    const result = formatSearchPreview('', 'test', 150);
    expect(result).toBe('');
  });

  it('handles empty query', () => {
    const content = 'Some content here';
    const result = formatSearchPreview(content, '', 150);
    // Empty query indexOf returns 0, so it will show context around position 0
    expect(result).toContain('Some content');
  });

  it('does not add trailing ellipsis when match context reaches end of content', () => {
    const content = 'Short text with target at end';
    const result = formatSearchPreview(content, 'end', 150);
    expect(result.endsWith('...')).toBe(false);
    expect(result).toContain('end');
  });
});
